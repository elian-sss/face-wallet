from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from .models import Profile
import face_recognition
import json
import numpy as np
import cv2

from django.contrib.auth.models import User
from .serializers import RegisterSerializer, FaceVerificationSerializer
from django.utils import timezone
from datetime import timedelta
from .services import send_whatsapp_code
from .serializers import (
    RegisterSerializer, PhoneVerificationSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny, )

    def perform_create(self, serializer):
        user = serializer.save()
        face_image = self.request.data.get('face_image')

        if face_image:
            try:
                image_bytes = face_image.read()
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                face_encodings = face_recognition.face_encodings(rgb_img)
                
                if not face_encodings:
                    raise ValueError("Nenhum rosto detectado na imagem.")

                embedding = face_encodings[0]
                
                Profile.objects.create(
                    user=user,
                    face_embedding=json.dumps(embedding.tolist())
                )
            except Exception as e:
                user.delete()
                raise serializers.ValidationError({"face_image": f"Erro no processamento facial: {e}"})

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
    
class FaceVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FaceVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        uploaded_image = request.data.get('face_image')

        try:
            profile = Profile.objects.get(user=user)
            stored_embedding_str = profile.face_embedding
            if not stored_embedding_str:
                return Response({"detail": "Nenhum rosto cadastrado para este usuário."}, status=400)
            
            stored_embedding = np.array(json.loads(stored_embedding_str))
            
            image_bytes = uploaded_image.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            face_encodings = face_recognition.face_encodings(rgb_img)
            if not face_encodings:
                return Response({"detail": "Nenhum rosto detectado na imagem enviada."}, status=400)

            new_embedding = face_encodings[0]

            results = face_recognition.compare_faces([stored_embedding], new_embedding, tolerance=0.50)
            
            if results[0]:
                return Response({"detail": "Rosto verificado com sucesso."}, status=200)
            else:
                return Response({"detail": "Verificação facial falhou. Os rostos não correspondem."}, status=400)

        except Profile.DoesNotExist:
            return Response({"detail": "Perfil não encontrado."}, status=404)
        except Exception as e:
            return Response({"detail": f"Ocorreu um erro durante a verificação: {e}"}, status=500)
        
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        phone_number = serializer.validated_data.pop('phone_number')
        face_image = serializer.validated_data.pop('face_image')
        user = serializer.save()

        embedding = None
        if face_image:
            try:
                image_bytes = face_image.read()
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                face_encodings = face_recognition.face_encodings(rgb_img)
                
                if not face_encodings:
                    user.delete()
                    raise serializers.ValidationError({"face_image": "Nenhum rosto detectado na imagem."})
                embedding = face_encodings[0]
            
            except Exception as e:
                user.delete()
                raise serializers.ValidationError({"face_image": f"Erro no processamento facial: {e}"})
        else:
             user.delete()
             raise serializers.ValidationError({"face_image": "A imagem facial é obrigatória."})

        profile = Profile.objects.create(
            user=user, 
            phone_number=phone_number, 
            face_embedding=json.dumps(embedding.tolist())
        )
        
        code, success = send_whatsapp_code(phone_number, user)
        
        if success:
            profile.verification_code = code
            profile.verification_expiry = timezone.now() + timedelta(minutes=10)
            profile.save()
        else:
            user.delete()
            raise serializers.ValidationError({"detail": "Não foi possível enviar o código de verificação. Tente novamente."})

class PhoneVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(username=username)
            profile = user.profile
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"detail": "Usuário não encontrado."}, status=404)

        if profile.is_verification_code_expired() or profile.verification_code != code:
            return Response({"detail": "Código inválido ou expirado."}, status=400)

        profile.is_phone_verified = True
        profile.verification_code = None
        profile.verification_expiry = None
        profile.save()

        return Response({"detail": "Telefone verificado com sucesso!"}, status=200)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'] # Agora usamos o email

        try:
            # Busca pelo usuário com o email (que é único)
            user = User.objects.get(email=email)
            profile = user.profile
            
            # Garante que o telefone daquele usuário específico está verificado
            if not profile.is_phone_verified:
                 return Response({"detail": "O telefone deste usuário não está verificado."}, status=400)

        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response({"detail": "Se uma conta com este e-mail existir, um código será enviado."}, status=200)

        # Pega o telefone do perfil encontrado e envia o código
        phone_number = profile.phone_number
        code, success = send_whatsapp_code(phone_number, user)

        if success:
            profile.verification_code = code
            profile.verification_expiry = timezone.now() + timedelta(minutes=10)
            profile.save()
        
        return Response({"detail": "Se uma conta com este e-mail existir, um código será enviado."}, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        password = serializer.validated_data['password']

        try:
            profile = Profile.objects.get(phone_number=phone_number)
            user = profile.user
        except Profile.DoesNotExist:
            return Response({"detail": "Código inválido ou expirado."}, status=400)

        if profile.is_verification_code_expired() or profile.verification_code != code:
            return Response({"detail": "Código inválido ou expirado."}, status=400)

        user.set_password(password)
        user.save()
        
        profile.verification_code = None
        profile.verification_expiry = None
        profile.save()

        return Response({"detail": "Senha redefinida com sucesso."}, status=200)