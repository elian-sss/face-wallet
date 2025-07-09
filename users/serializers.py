from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, validators

class RegisterSerializer(serializers.ModelSerializer):
    face_image = serializers.ImageField(write_only=True, required=True)
    phone_number = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'face_image', 'phone_number')
        
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        User.objects.all(), "Um usuário com este e-mail já existe."
                    )
                ]
            }
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return user
    
class FaceVerificationSerializer(serializers.Serializer):
    face_image = serializers.ImageField(write_only=True, required=True)

class PhoneVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required=True, max_length=6)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True, max_length=6)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não correspondem."})
        return attrs