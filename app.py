from flask import Flask, redirect, url_for, request, jsonify
from config import Config
from models import db
from blueprints.admin import admin_bp
from blueprints.bot import bot_bp
from webhook_simple import webhook_bp
app.register_blueprint(webhook_bp)
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)
    
    # Try to import WhatsApp blueprint
    try:
        from blueprints.whatsapp import whatsapp_bp
        app.register_blueprint(whatsapp_bp)
        print("✓ WhatsApp blueprint registered successfully")
    except Exception as e:
        print(f"✗ Failed to register WhatsApp blueprint: {e}")
        
        # Fallback: Add webhook routes directly
        @app.route('/webhook', methods=['GET'])
        def verify_webhook():
            """Verify webhook for WhatsApp"""
            verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'token123')
            
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            if mode and token:
                if mode == 'subscribe' and token == verify_token:
                    print('WEBHOOK_VERIFIED')
                    return challenge, 200
                else:
                    return 'Forbidden', 403
            
            return 'Bad Request', 400
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle incoming WhatsApp messages"""
            return jsonify({'status': 'ok'}), 200
    
    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('admin.index'))
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    # Debug endpoint
    @app.route('/debug')
    def debug():
        rules = []
        for rule in app.url_map.iter_rules():
            rules.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        return jsonify({
            'status': 'debug info',
            'routes': rules,
            'blueprints': list(app.blueprints.keys())
        })
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)