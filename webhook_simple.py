from flask import Blueprint, request

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET'])
def verify():
    """Simple webhook verification"""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == 'Token-123':
        return challenge
    return 'Forbidden', 403

@webhook_bp.route('/webhook', methods=['POST'])
def receive():
    """Receive webhook events"""
    return {'status': 'ok'}, 200