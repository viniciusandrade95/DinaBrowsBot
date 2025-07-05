import openai
from models import BusinessConfig, Service, OperatingHours
from config import Config

class BrowStudioBot:
    def __init__(self, business_id=1):
        self.business_id = business_id
        self.business = BusinessConfig.query.get(business_id)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=Config.AI_API_KEY,
            base_url=Config.AI_BASE_URL,
        )
        
        # Session state
        self.session_state = {
            "greeted": False,
            "services_discussed": [],
            "context": []
        }
        
    def _get_business_info(self):
        """Retrieve current business configuration from database"""
        self.business = BusinessConfig.query.get(self.business_id)
        if not self.business:
            return None
        
        # Get services
        services = Service.query.filter_by(business_id=self.business_id, active=True).all()
        
        # Get operating hours
        hours = OperatingHours.query.filter_by(business_id=self.business_id).order_by(OperatingHours.day_of_week).all()
        
        return {
            "name": self.business.studio_name,
            "address": self.business.address,
            "phone": self.business.phone,
            "whatsapp": self.business.whatsapp,
            "website": self.business.website,
            "services": services,
            "hours": hours,
            "bot_tone": self.business.bot_tone,
            "bot_intro": self.business.bot_intro_message
        }
    
    def _format_services_text(self, services):
        """Format services for display"""
        text = ""
        for service in services:
            text += f"- {service.name}: R$ {service.price:.2f} (duração: {service.duration_minutes}min)\n"
        return text
    
    def _format_hours_text(self, hours):
        """Format operating hours for display"""
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        text = ""
        for hour in hours:
            if not hour.is_closed:
                text += f"{days[hour.day_of_week]}: {hour.open_time} - {hour.close_time}\n"
            else:
                text += f"{days[hour.day_of_week]}: Fechado\n"
        return text
    
    def _extract_service_from_message(self, message, services):
        """Find service mentioned in message"""
        message_lower = message.lower()
        for service in services:
            if service.name.lower() in message_lower:
                return service
        return None
    
    def _generate_system_prompt(self, info):
        """Generate system prompt based on business configuration"""
        prompt = f"""Você é uma atendente virtual do {info['name']}.

INFORMAÇÕES DO STUDIO:
- Nome: {info['name']}
- Endereço: {info['address']}
- Telefone: {info['phone']}
- WhatsApp: {info['whatsapp']}
{'- Website: ' + info['website'] if info['website'] else ''}

HORÁRIO DE FUNCIONAMENTO:
{self._format_hours_text(info['hours'])}

SERVIÇOS OFERECIDOS:
{self._format_services_text(info['services'])}

TOM DE CONVERSA:
{info['bot_tone'] or 'Seja simpática, profissional e prestativa.'}

INSTRUÇÕES:
1. Responda APENAS em português brasileiro
2. Mantenha o tom definido acima
3. Responda APENAS perguntas relacionadas aos serviços do studio
4. Para agendamentos, peça para entrar em contato via WhatsApp
5. Use emojis ocasionalmente para tornar a conversa mais amigável"""
        
        return prompt
    
    def get_response(self, user_message):
        """Generate response to user message"""
        info = self._get_business_info()
        if not info:
            return "Desculpe, não consegui acessar as informações do studio."
        
        # Check for greetings
        greetings = ['oi', 'olá', 'bom dia', 'boa tarde', 'boa noite', 'ola']
        if any(greeting in user_message.lower() for greeting in greetings):
            if not self.session_state['greeted']:
                self.session_state['greeted'] = True
                if info['bot_intro']:
                    return info['bot_intro']
                else:
                    return f"Olá! Seja bem-vinda ao {info['name']}! Como posso ajudar você hoje? 😊"
        
        # Check for service questions
        service = self._extract_service_from_message(user_message, info['services'])
        if service:
            if service.id in self.session_state['services_discussed']:
                return f"Já conversamos sobre {service.name}! Gostaria de agendar ou conhecer outro serviço? ✨"
            else:
                self.session_state['services_discussed'].append(service.id)
                response = f"{service.name}: R$ {service.price:.2f} - Duração: {service.duration_minutes} minutos"
                if service.description:
                    response += f"\n{service.description}"
                response += "\n\nGostaria de agendar esse serviço?"
                return response
        
        # Check for hours question
        hours_keywords = ['horário', 'horario', 'quando', 'abre', 'fecha', 'funcionamento']
        if any(keyword in user_message.lower() for keyword in hours_keywords):
            return f"Nossos horários de funcionamento:\n\n{self._format_hours_text(info['hours'])}\n\nQuer agendar um horário?"
        
        # Check for price questions without specific service
        price_keywords = ['quanto custa', 'preço', 'valor', 'precos']
        if any(keyword in user_message.lower() for keyword in price_keywords) and not service:
            return f"Temos vários serviços! Aqui estão nossos preços:\n\n{self._format_services_text(info['services'])}\n\nQual serviço te interessou?"
        
        # For other questions, use AI if available
        try:
            if Config.AI_API_KEY and Config.AI_API_KEY != 'your-api-key-here':
                response = self.client.chat.completions.create(
                    model=Config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": self._generate_system_prompt(info)},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content
            else:
                # Fallback response when AI is not configured
                return self._get_fallback_response(user_message, info)
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_response(user_message, info)
    
    def _get_fallback_response(self, message, info):
        """Fallback responses when AI is not available"""
        message_lower = message.lower()
        
        # Contact questions
        if any(word in message_lower for word in ['contato', 'telefone', 'whatsapp', 'ligar']):
            return f"Entre em contato conosco:\n📱 WhatsApp: {info['whatsapp']}\n📞 Telefone: {info['phone']}"
        
        # Location questions
        if any(word in message_lower for word in ['onde', 'endereço', 'endereco', 'localização']):
            return f"Estamos localizados em:\n📍 {info['address']}"
        
        # Default response
        return "Posso te ajudar com informações sobre nossos serviços, preços, horários ou agendamento. O que gostaria de saber? 😊"