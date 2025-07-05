from . import db
from datetime import datetime

class BusinessConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studio_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300))
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    website = db.Column(db.String(200))
    bot_tone = db.Column(db.Text)
    bot_intro_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='business', lazy=True, cascade='all, delete-orphan')
    operating_hours = db.relationship('OperatingHours', backref='business', lazy=True, cascade='all, delete-orphan')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_config.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)

class OperatingHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_config.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    open_time = db.Column(db.String(5))  # Format: "09:00"
    close_time = db.Column(db.String(5))  # Format: "18:00"
    is_closed = db.Column(db.Boolean, default=False)