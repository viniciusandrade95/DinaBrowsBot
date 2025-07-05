import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///brow_studio.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI/Together AI settings
    AI_API_KEY = os.environ.get('AI_API_KEY') or 'your-api-key-here'
    AI_BASE_URL = os.environ.get('AI_BASE_URL') or 'https://api.together.xyz/v1'
    AI_MODEL = os.environ.get('AI_MODEL') or 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'
    
    # WhatsApp Business API settings
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')  # Your WhatsApp Business API Token
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')  # Phone number ID from Meta
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')  # For webhook verification
    WHATSAPP_API_VERSION = os.environ.get('WHATSAPP_API_VERSION') or 'v18.0'