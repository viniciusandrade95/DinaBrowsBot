from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import db, BusinessConfig, Service, OperatingHours

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def index():
    """Admin panel home page"""
    business = BusinessConfig.query.first()
    services = Service.query.filter_by(business_id=1).all() if business else []
    hours = OperatingHours.query.filter_by(business_id=1).order_by(OperatingHours.day_of_week).all() if business else []
    
    # Create default business if none exists
    if not business:
        business = BusinessConfig(
            studio_name="Meu Studio de Sobrancelhas",
            address="",
            phone="",
            whatsapp="",
            bot_tone="Seja simpática, profissional e prestativa.",
            bot_intro_message="Olá! Seja bem-vinda ao nosso studio! Como posso ajudar você hoje? 😊"
        )
        db.session.add(business)
        db.session.commit()
        
        # Create default hours
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for i in range(7):
            hour = OperatingHours(
                business_id=business.id,
                day_of_week=i,
                open_time="09:00" if i < 5 else "09:00" if i == 5 else "",
                close_time="18:00" if i < 5 else "16:00" if i == 5 else "",
                is_closed=True if i == 6 else False
            )
            db.session.add(hour)
        db.session.commit()
    
    return render_template('admin.html', business=business, services=services, hours=hours)

@admin_bp.route('/update-business', methods=['POST'])
def update_business():
    """Update business information"""
    data = request.json
    business = BusinessConfig.query.first()
    
    if business:
        business.studio_name = data.get('studio_name', business.studio_name)
        business.address = data.get('address', business.address)
        business.phone = data.get('phone', business.phone)
        business.whatsapp = data.get('whatsapp', business.whatsapp)
        business.website = data.get('website', business.website)
        business.bot_tone = data.get('bot_tone', business.bot_tone)
        business.bot_intro_message = data.get('bot_intro_message', business.bot_intro_message)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Informações atualizadas com sucesso!'})
    
    return jsonify({'success': False, 'message': 'Erro ao atualizar informações'})

@admin_bp.route('/update-hours', methods=['POST'])
def update_hours():
    """Update operating hours"""
    data = request.json
    hours_data = data.get('hours', [])
    
    for hour_info in hours_data:
        hour = OperatingHours.query.get(hour_info['id'])
        if hour:
            hour.open_time = hour_info.get('open_time', hour.open_time)
            hour.close_time = hour_info.get('close_time', hour.close_time)
            hour.is_closed = hour_info.get('is_closed', hour.is_closed)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Horários atualizados com sucesso!'})

@admin_bp.route('/add-service', methods=['POST'])
def add_service():
    """Add a new service"""
    data = request.json
    
    service = Service(
        business_id=1,
        name=data['name'],
        price=float(data['price']),
        duration_minutes=int(data['duration']),
        description=data.get('description', '')
    )
    
    db.session.add(service)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Serviço adicionado com sucesso!',
        'service': {
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'duration_minutes': service.duration_minutes
        }
    })

@admin_bp.route('/update-service/<int:service_id>', methods=['POST'])
def update_service(service_id):
    """Update a service"""
    data = request.json
    service = Service.query.get(service_id)
    
    if service:
        service.name = data.get('name', service.name)
        service.price = float(data.get('price', service.price))
        service.duration_minutes = int(data.get('duration', service.duration_minutes))
        service.description = data.get('description', service.description)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Serviço atualizado com sucesso!'})
    
    return jsonify({'success': False, 'message': 'Serviço não encontrado'})

@admin_bp.route('/delete-service/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """Delete a service"""
    service = Service.query.get(service_id)
    
    if service:
        db.session.delete(service)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Serviço removido com sucesso!'})
    
    return jsonify({'success': False, 'message': 'Serviço não encontrado'})