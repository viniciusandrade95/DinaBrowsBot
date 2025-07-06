from flask import Flask, redirect, url_for, request, jsonify
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///brow_studio.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    try:
        # Try to import and initialize database
        from models import db
        db.init_app(app)
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        # Continue without database for now
    
    # Register blueprints with error handling
    try:
        from blueprints.admin import admin_bp
        app.register_blueprint(admin_bp)
        logger.info("✓ Admin blueprint registered")
    except Exception as e:
        logger.error(f"✗ Admin blueprint failed: {e}")
    
    try:
        from blueprints.bot import bot_bp
        app.register_blueprint(bot_bp)
        logger.info("✓ Bot blueprint registered")
    except Exception as e:
        logger.error(f"✗ Bot blueprint failed: {e}")
    
    # WhatsApp webhook routes (simplified, no dependencies)
    @app.route('/webhook', methods=['GET'])
    def verify_webhook():
        """Verify webhook for WhatsApp"""
        verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'token123')
        
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        logger.info(f"Webhook verification: mode={mode}, token_match={token == verify_token}")
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                logger.info('WEBHOOK_VERIFIED')
                return challenge, 200
            else:
                return 'Forbidden', 403
        
        return 'Bad Request', 400
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle incoming WhatsApp messages"""
        try:
            data = request.get_json()
            logger.info(f"Received webhook data: {data}")
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({'status': 'error'}), 200
    
    # Root route
    @app.route('/')
    def index():
        return '''
        <h1>🌟 Brow Studio Bot is Running! 🌟</h1>
        <p><strong>Webhook URL:</strong> /webhook</p>
        <p><strong>Health Check:</strong> /health</p>
        <p><strong>Admin Panel:</strong> /admin</p>
        '''
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'brow-studio-bot',
            'version': '1.0.0'
        }, 200
    
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
            'blueprints': list(app.blueprints.keys()),
            'env_vars': {
                'PORT': os.environ.get('PORT'),
                'DATABASE_URL': bool(os.environ.get('DATABASE_URL')),
                'WHATSAPP_VERIFY_TOKEN': bool(os.environ.get('WHATSAPP_VERIFY_TOKEN'))
            }
        })
    
    # Create tables if database is available
    try:
        with app.app_context():
            from models import db
            db.create_all()
            logger.info("✓ Database tables created")
    except Exception as e:
        logger.error(f"✗ Database table creation failed: {e}")
    
    return app

# Create app instance for Gunicorn
try:
    application = create_app()
    logger.info("✓ Application created successfully")
except Exception as e:
    logger.error(f"✗ Failed to create application: {e}")
    # Create a minimal app to show the error
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"Application failed to start: {str(e)}", 500
    
    @application.route('/health')
    def health():
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    application.run(debug=debug, host='0.0.0.0', port=port)