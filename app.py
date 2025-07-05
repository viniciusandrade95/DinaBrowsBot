from flask import Flask, redirect, url_for
from config import Config
from models import db
from blueprints.admin import admin_bp
from blueprints.bot import bot_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)
    
    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('admin.index'))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)