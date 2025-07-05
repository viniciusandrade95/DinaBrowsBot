from flask import Blueprint, request, jsonify, session
from bot_logic import BrowStudioBot
import uuid

bot_bp = Blueprint('bot', __name__, url_prefix='/bot')

# Store bot instances for each session
bot_instances = {}

@bot_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    message = data.get('message', '')
    
    # Get or create session ID
    session_id = session.get('bot_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['bot_session_id'] = session_id
    
    # Get or create bot instance for this session
    if session_id not in bot_instances:
        bot_instances[session_id] = BrowStudioBot()
    
    bot = bot_instances[session_id]
    
    # Get response
    response = bot.get_response(message)
    
    return jsonify({
        'success': True,
        'response': response,
        'session_id': session_id
    })

@bot_bp.route('/reset', methods=['POST'])
def reset():
    """Reset bot session"""
    session_id = session.get('bot_session_id')
    
    if session_id and session_id in bot_instances:
        # Create new bot instance
        bot_instances[session_id] = BrowStudioBot()
        return jsonify({'success': True, 'message': 'Sessão reiniciada'})
    
    return jsonify({'success': False, 'message': 'Nenhuma sessão ativa'})

@bot_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify bot is working"""
    try:
        bot = BrowStudioBot()
        return jsonify({
            'success': True,
            'message': 'Bot está funcionando!',
            'test_response': bot.get_response('Olá')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })