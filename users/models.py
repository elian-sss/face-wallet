from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_embedding = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def is_verification_code_expired(self):
        if self.verification_expiry and self.verification_expiry < timezone.now():
            return True
        return False