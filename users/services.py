import requests
from django.conf import settings
import random

def send_whatsapp_code(phone_number, user):
    code = str(random.randint(100000, 999999))
    message = f"Olá {user.first_name}, seu código de verificação para a Carteira Digital é: *{code}*"

    api_url = settings.EVOLUTION_API_URL
    api_key = settings.EVOLUTION_API_KEY
    instance_name = settings.EVOLUTION_INSTANCE_NAME

    url = f"{api_url}/message/sendText/{instance_name}"

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "number": phone_number,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": message
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return code, True 
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem para a Evolution API: {e}")
        return None, False 