import requests
import json
from config import Config

class WhatsAppService:
    def __init__(self):
        self.token = Config.WHATSAPP_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
        self.api_version = Config.WHATSAPP_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        
    def send_message(self, to_number, message):
        """Send a text message via WhatsApp"""
        url = f"{self.base_url}/messages"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending WhatsApp message: {e}")
            return None
    
    def send_template_message(self, to_number, template_name, language_code="pt_BR"):
        """Send a template message (for initial contact)"""
        url = f"{self.base_url}/messages"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending template message: {e}")
            return None
    
    def mark_as_read(self, message_id):
        """Mark a message as read"""
        url = f"{self.base_url}/messages"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except:
            return False
    
    def send_typing_indicator(self, to_number):
        """Show typing indicator"""
        url = f"{self.base_url}/messages"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "typing": "on"
        }
        
        try:
            requests.post(url, headers=headers, json=data)
        except:
            pass