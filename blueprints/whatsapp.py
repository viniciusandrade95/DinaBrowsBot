from flask import Blueprint, request, jsonify
from config import Config
from bot_logic import BrowStudioBot
from services.whatsapp import WhatsAppService
import json
import time

whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/webhook')

# Store bot instances per phone number
bot_sessions = {}

# Initialize WhatsApp service
wa_service = WhatsAppService()

@whatsapp_bp.route('/', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp Business API"""
    verify_token = Config.WHATSAPP_VERIFY_TOKEN
    
    # Parse params from the webhook verification request
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == 'subscribe' and token == verify_token:
            # Respond with 200 OK and challenge token from the request
            print('WEBHOOK_VERIFIED')
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            return 'Forbidden', 403
    
    return 'Bad Request', 400

@whatsapp_bp.route('/', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get the webhook data
        data = request.get_json()
        
        # Extract the message details
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # Check if it's a message
                    if 'messages' in value:
                        for message in value['messages']:
                            handle_message(message, value.get('metadata', {}))
                    
                    # Check if it's a status update
                    elif 'statuses' in value:
                        for status in value['statuses']:
                            handle_status(status)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error'}), 200

def handle_message(message, metadata):
    """Process incoming WhatsApp message"""
    try:
        # Extract message details
        from_number = message.get('from')
        message_id = message.get('id')
        timestamp = message.get('timestamp')
        message_type = message.get('type')
        
        # Mark message as read
        wa_service.mark_as_read(message_id)
        
        # Handle different message types
        if message_type == 'text':
            text = message.get('text', {}).get('body', '')
            
            # Show typing indicator
            wa_service.send_typing_indicator(from_number)
            
            # Get or create bot session for this user
            if from_number not in bot_sessions:
                bot_sessions[from_number] = BrowStudioBot()
            
            bot = bot_sessions[from_number]
            
            # Get bot response
            response = bot.get_response(text)
            
            # Send response
            wa_service.send_message(from_number, response)
            
        elif message_type == 'button':
            # Handle button responses
            button_text = message.get('button', {}).get('text', '')
            handle_button_response(from_number, button_text)
            
        else:
            # Handle other message types (image, audio, etc.)
            wa_service.send_message(
                from_number, 
                "Desculpe, no momento só consigo processar mensagens de texto. Por favor, digite sua pergunta! 😊"
            )
            
    except Exception as e:
        print(f"Error handling message: {e}")
        # Send error message to user
        try:
            wa_service.send_message(
                from_number,
                "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente!"
            )
        except:
            pass

def handle_status(status):
    """Handle message status updates"""
    status_type = status.get('status')
    message_id = status.get('id')
    recipient_id = status.get('recipient_id')
    timestamp = status.get('timestamp')
    
    # Log status updates (you can store these in database if needed)
    print(f"Message {message_id} to {recipient_id} is {status_type} at {timestamp}")

def handle_button_response(from_number, button_text):
    """Handle button click responses"""
    # Get bot session
    if from_number not in bot_sessions:
        bot_sessions[from_number] = BrowStudioBot()
    
    bot = bot_sessions[from_number]
    
    # Process button as regular text
    response = bot.get_response(button_text)
    wa_service.send_message(from_number, response)

@whatsapp_bp.route('/send-test', methods=['POST'])
def send_test_message():
    """Test endpoint to send a WhatsApp message"""
    data = request.json
    to_number = data.get('to')
    message = data.get('message', 'Teste do Bot de Sobrancelhas! 🌟')
    
    if not to_number:
        return jsonify({'error': 'Phone number required'}), 400
    
    result = wa_service.send_message(to_number, message)
    
    if result:
        return jsonify({'success': True, 'result': result}), 200
    else:
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500