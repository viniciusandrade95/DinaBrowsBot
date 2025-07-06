from flask import Blueprint, request, jsonify, session
import uuid
import logging

logger = logging.getLogger(__name__)

bot_bp = Blueprint('bot', __name__, url_prefix='/bot')

# Store bot instances for each session
bot_instances = {}

@bot_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        
        # Get or create session ID
        session_id = session.get('bot_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['bot_session_id'] = session_id
        
        # Get or create bot instance for this session
        if session_id not in bot_instances:
            from bot_logic import BrowStudioBot
            bot_instances[session_id] = BrowStudioBot()
        
        bot = bot_instances[session_id]
        
        # Get response
        response = bot.get_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        })

@bot_bp.route('/reset', methods=['POST'])
def reset():
    """Reset bot session"""
    try:
        session_id = session.get('bot_session_id')
        
        if session_id and session_id in bot_instances:
            # Create new bot instance
            from bot_logic import BrowStudioBot
            bot_instances[session_id] = BrowStudioBot()
            return jsonify({'success': True, 'message': 'Sessão reiniciada'})
        
        return jsonify({'success': False, 'message': 'Nenhuma sessão ativa'})
        
    except Exception as e:
        logger.error(f"Error resetting chat: {e}")
        return jsonify({'success': False, 'error': str(e)})

@bot_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify bot is working"""
    try:
        from bot_logic import BrowStudioBot
        bot = BrowStudioBot()
        return jsonify({
            'success': True,
            'message': 'Bot está funcionando!',
            'test_response': bot.get_response('Olá')
        })
    except Exception as e:
        logger.error(f"Error in bot test: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })