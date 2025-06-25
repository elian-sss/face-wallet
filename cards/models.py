from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_holder_name = models.CharField(max_length=255)
    card_number = models.CharField(max_length=255)
    expiry_date = models.CharField(max_length=255)
    cvv = models.CharField(max_length=255)         
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Card for {self.user.username}"