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

from .serializers import RegisterSerializer, FaceVerificationSerializer

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