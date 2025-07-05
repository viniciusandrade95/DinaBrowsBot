from flask import Flask, redirect, url_for
from config import Config
from models import db
from blueprints.admin import admin_bp
from blueprints.bot import bot_bp
from blueprints.whatsapp import whatsapp_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(whatsapp_bp)
    
    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('admin.index'))
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)