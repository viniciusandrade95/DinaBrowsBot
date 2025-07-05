from flask import Flask, request
import os

application = Flask(__name__)

@application.route('/')
def index():
    return "Brow Studio Bot is running!"

@application.route('/health')
def health():
    return {'status': 'healthy'}, 200

@application.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp"""
    verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'token123')
    
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        else:
            return 'Forbidden', 403
    
    return 'Bad Request', 400

@application.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port)
