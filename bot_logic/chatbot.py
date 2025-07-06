from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BrowStudioBot:
    def __init__(self, business_id=1):
        self.business_id = business_id
        
        # Enhanced session state
        self.session_state = {
            "greeted": False,
            "greeting_count": 0,
            "services_discussed": [],
            "last_intent": None,
            "conversation_history": []
        }
        
        # Default business info (fallback)
        self.default_info = {
            "name": "Meu Studio de Sobrancelhas",
            "address": "Endereço não configurado",
            "phone": "(11) 99999-9999",
            "whatsapp": "(11) 99999-9999",
            "services": [
                {"name": "Design de Sobrancelhas", "price": 50.0, "duration": 60},
                {"name": "Henna", "price": 30.0, "duration": 45},
                {"name": "Micropigmentação", "price": 200.0, "duration": 120}
            ],
            "hours": "Segunda a Sexta: 9h às 18h\nSábado: 9h às 16h\nDomingo: Fechado",
            "bot_intro": "Olá! Seja bem-vinda ao nosso studio! Como posso ajudar você hoje? 😊"
        }
        
    def _get_business_info(self):
        """Retrieve business configuration with fallback"""
        try:
            # Try to get from database
            from models import BusinessConfig, Service, OperatingHours
            business = BusinessConfig.query.get(self.business_id)
            
            if business:
                services = Service.query.filter_by(business_id=self.business_id, active=True).all()
                hours = OperatingHours.query.filter_by(business_id=self.business_id).order_by(OperatingHours.day_of_week).all()
                
                return {
                    "name": business.studio_name,
                    "address": business.address,
                    "phone": business.phone,
                    "whatsapp": business.whatsapp,
                    "website": business.website,
                    "services": services,
                    "hours": hours,
                    "bot_intro": business.bot_intro_message
                }
        except Exception as e:
            logger.warning(f"Could not access database, using defaults: {e}")
        
        # Return default info
        return self.default_info
    
    def _format_services_text(self, services):
        """Format services for display"""
        if not services:
            return "Ainda não temos serviços cadastrados."
        
        text = ""
        for service in services:
            if hasattr(service, 'name'):  # Database object
                text += f"• {service.name}: R$ {service.price:.2f} (duração: {service.duration_minutes}min)\n"
                if hasattr(service, 'description') and service.description:
                    text += f"  {service.description}\n"
            else:  # Default dict
                text += f"• {service['name']}: R$ {service['price']:.2f} (duração: {service['duration']}min)\n"
        
        return text.strip()
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Greetings
        greetings = ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hi', 'hey']
        if any(greeting in message_lower.split() for greeting in greetings):
            return 'greeting'
        
        # Hours/Schedule
        if any(word in message_lower for word in ['horário', 'horario', 'quando', 'abre', 'fecha', 'funcionamento', 'aberto']):
            return 'hours'
        
        # Price inquiry
        if any(word in message_lower for word in ['quanto custa', 'preço', 'valor', 'precos', 'quanto é']):
            return 'price'
        
        # Service inquiry
        if any(word in message_lower for word in ['serviço', 'servico', 'procedimento', 'oferece', 'fazem', 'disponível']):
            return 'services'
        
        # Contact
        if any(word in message_lower for word in ['contato', 'telefone', 'whatsapp', 'ligar', 'zap']):
            return 'contact'
        
        # Location
        if any(word in message_lower for word in ['onde', 'endereço', 'endereco', 'localização', 'localizacao', 'fica']):
            return 'location'
        
        # Booking
        if any(word in message_lower for word in ['agendar', 'agendamento', 'marcar', 'horário disponível']):
            return 'booking'
        
        return 'unknown'
    
    def get_response(self, user_message):
        """Generate response to user message"""
        info = self._get_business_info()
        
        # Add to conversation history
        self.session_state['conversation_history'].append({
            'user': user_message,
            'timestamp': datetime.now()
        })
        
        # Detect intent
        intent = self._detect_intent(user_message)
        
        # Handle greetings specially
        if intent == 'greeting':
            self.session_state['greeting_count'] += 1
            
            if not self.session_state['greeted']:
                self.session_state['greeted'] = True
                return info.get('bot_intro', f"Olá! Seja bem-vinda ao {info['name']}! 😊 Como posso ajudar você hoje?")
            elif self.session_state['greeting_count'] == 2:
                return "Oi novamente! 😊 Em que posso ajudar? Temos diversos serviços de sobrancelhas disponíveis."
            else:
                return "Olá! Posso te ajudar com informações sobre nossos serviços, preços ou agendamento? 😊"
        
        # Handle specific intents
        if intent == 'hours':
            hours_text = info.get('hours', 'Horários não configurados')
            if isinstance(hours_text, str):
                return f"Nossos horários de funcionamento:\n\n{hours_text}\n\nPara agendar, entre em contato pelo WhatsApp: {info['whatsapp']} 📱"
            else:
                # Format database hours
                days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                formatted_hours = ""
                for hour in hours_text:
                    day_name = days[hour.day_of_week]
                    if not hour.is_closed:
                        formatted_hours += f"{day_name}: {hour.open_time} - {hour.close_time}\n"
                    else:
                        formatted_hours += f"{day_name}: Fechado\n"
                return f"Nossos horários de funcionamento:\n\n{formatted_hours}\n\nPara agendar, entre em contato pelo WhatsApp: {info['whatsapp']} 📱"
        
        elif intent == 'services':
            services_text = self._format_services_text(info['services'])
            return f"Nossos serviços:\n\n{services_text}\n\nQual serviço te interessou? 😊"
        
        elif intent == 'price':
            services_text = self._format_services_text(info['services'])
            return f"Aqui estão nossos preços:\n\n{services_text}\n\nQual serviço você gostaria de saber mais detalhes?"
        
        elif intent == 'contact':
            contact_info = f"📱 WhatsApp: {info['whatsapp']}\n📞 Telefone: {info['phone']}"
            if info.get('website'):
                contact_info += f"\n🌐 Site: {info['website']}"
            return f"Entre em contato conosco:\n\n{contact_info}\n\nPrefere agendar por WhatsApp para atendimento mais rápido!"
        
        elif intent == 'location':
            return f"📍 Estamos localizados em:\n{info['address']}\n\nFácil acesso e estacionamento próximo!"
        
        elif intent == 'booking':
            return f"Para agendar seu horário, entre em contato pelo WhatsApp: {info['whatsapp']} 📱\n\nNosso atendimento é rápido e personalizado!"
        
        # Default response
        return "Posso te ajudar com:\n• Informações sobre serviços e preços\n• Horários de funcionamento\n• Localização do studio\n• Contato para agendamento\n\nO que você gostaria de saber? 😊"