from rest_framework import serializers
from django.conf import settings
from cryptography.fernet import Fernet

from .models import Card

key = settings.ENCRYPTION_KEY.encode('utf-8')
cipher_suite = Fernet(key)

class CardSerializer(serializers.ModelSerializer):
    card_holder_name = serializers.CharField()
    card_number = serializers.CharField()
    expiry_date = serializers.CharField()
    cvv = serializers.CharField(write_only=True)

    class Meta:
        model = Card
        fields = ('id', 'card_holder_name', 'card_number', 'expiry_date', 'cvv')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user

        validated_data['card_holder_name'] = cipher_suite.encrypt(validated_data['card_holder_name'].encode('utf-8')).decode('utf-8')
        validated_data['card_number'] = cipher_suite.encrypt(validated_data['card_number'].encode('utf-8')).decode('utf-8')
        validated_data['expiry_date'] = cipher_suite.encrypt(validated_data['expiry_date'].encode('utf-8')).decode('utf-8')
        validated_data['cvv'] = cipher_suite.encrypt(validated_data['cvv'].encode('utf-8')).decode('utf-8')
        
        return super().create(validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        try:
            ret['card_holder_name'] = cipher_suite.decrypt(ret['card_holder_name'].encode('utf-8')).decode('utf-8')
            ret['card_number'] = cipher_suite.decrypt(ret['card_number'].encode('utf-8')).decode('utf-8')
            ret['expiry_date'] = cipher_suite.decrypt(ret['expiry_date'].encode('utf-8')).decode('utf-8')
        except Exception as e:
            for field in ['card_holder_name', 'card_number', 'expiry_date']:
                ret[field] = "Error decrypting data"
                
        return ret