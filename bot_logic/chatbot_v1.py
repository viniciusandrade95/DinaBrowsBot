import openai
from models import BusinessConfig, Service, OperatingHours
from config import Config
from datetime import datetime

class BrowStudioBot:
    def __init__(self, business_id=1):
        self.business_id = business_id
        self.business = BusinessConfig.query.get(business_id)
        
        # Initialize OpenAI client with error handling
        try:
            self.client = openai.OpenAI(
                api_key=Config.AI_API_KEY,
                base_url=Config.AI_BASE_URL,
            )
        except Exception as e:
            print(f"Warning: Could not initialize AI client: {e}")
            print("Bot will work with fallback responses only.")
            self.client = None
        
        # Enhanced session state
        self.session_state = {
            "greeted": False,
            "greeting_count": 0,
            "services_discussed": [],
            "last_intent": None,
            "conversation_history": []
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
        if not services:
            return "Ainda não temos serviços cadastrados."
        
        text = ""
        for service in services:
            text += f"• {service.name}: R$ {service.price:.2f} (duração: {service.duration_minutes}min)\n"
            if service.description:
                text += f"  {service.description}\n"
        return text.strip()
    
    def _format_hours_text(self, hours):
        """Format operating hours for display"""
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        today = datetime.now().weekday()
        text = ""
        
        for hour in hours:
            day_name = days[hour.day_of_week]
            if hour.day_of_week == today:
                day_name += " (HOJE)"
            
            if not hour.is_closed:
                text += f"{day_name}: {hour.open_time} - {hour.close_time}\n"
            else:
                text += f"{day_name}: Fechado\n"
        return text.strip()
    
    def _extract_service_from_message(self, message, services):
        """Find service mentioned in message"""
        message_lower = message.lower()
        for service in services:
            service_name_lower = service.name.lower()
            # Check for exact or partial matches
            if service_name_lower in message_lower or any(word in message_lower for word in service_name_lower.split()):
                return service
        return None
    
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
        
        # Help
        if any(word in message_lower for word in ['ajuda', 'ajudar', 'help', 'dúvida', 'duvida']):
            return 'help'
        
        # Date/Day
        if any(word in message_lower for word in ['que dia', 'hoje', 'data']):
            return 'date'
        
        return 'unknown'
    
    def _generate_system_prompt(self, info):
        """Generate system prompt based on business configuration"""
        services_list = "\n".join([f"- {s.name}: R$ {s.price:.2f} ({s.duration_minutes}min)" for s in info['services']])
        
        prompt = f"""Você é uma atendente virtual do {info['name']}.

REGRAS IMPORTANTES:
1. NUNCA invente serviços que não estão na lista abaixo
2. Seja consistente e profissional
3. Use APENAS as informações fornecidas
4. Responda APENAS em português brasileiro
5. Se repetir saudações, seja breve e sugira como pode ajudar

INFORMAÇÕES DO STUDIO:
Nome: {info['name']}
Endereço: {info['address']}
Telefone: {info['phone']}
WhatsApp: {info['whatsapp']}

SERVIÇOS DISPONÍVEIS (USE APENAS ESTES):
{services_list}

HORÁRIOS:
{self._format_hours_text(info['hours'])}

TOM: {info['bot_tone'] or 'Profissional e amigável'}

Para agendamentos, sempre direcione para o WhatsApp."""
        
        return prompt
    
    def get_response(self, user_message):
        """Generate response to user message"""
        info = self._get_business_info()
        if not info:
            return "Desculpe, não consegui acessar as informações do studio."
        
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
                if info['bot_intro']:
                    return info['bot_intro']
                else:
                    return f"Olá! Seja bem-vinda ao {info['name']}! 😊 Como posso ajudar você hoje?"
            elif self.session_state['greeting_count'] == 2:
                return "Oi novamente! 😊 Em que posso ajudar? Temos diversos serviços de sobrancelhas e cílios disponíveis."
            elif self.session_state['greeting_count'] >= 3:
                return "Olá! Vejo que está tentando cumprimentar várias vezes. Posso te ajudar com informações sobre nossos serviços, preços ou agendamento? 😊"
        
        # Handle specific intents with fallback responses
        if intent == 'hours':
            return f"Nossos horários de funcionamento:\n\n{self._format_hours_text(info['hours'])}\n\nPara agendar, entre em contato pelo WhatsApp: {info['whatsapp']} 📱"
        
        elif intent == 'services':
            services_text = self._format_services_text(info['services'])
            return f"Nossos serviços:\n\n{services_text}\n\nQual serviço te interessou? 😊"
        
        elif intent == 'price':
            # Check if asking about specific service
            service = self._extract_service_from_message(user_message, info['services'])
            if service:
                return f"{service.name}: R$ {service.price:.2f}\nDuração: {service.duration_minutes} minutos\n\nGostaria de agendar este serviço? Entre em contato pelo WhatsApp: {info['whatsapp']}"
            else:
                services_text = self._format_services_text(info['services'])
                return f"Aqui estão nossos preços:\n\n{services_text}\n\nQual serviço você gostaria de saber mais detalhes?"
        
        elif intent == 'contact':
            contact_info = f"📱 WhatsApp: {info['whatsapp']}\n📞 Telefone: {info['phone']}"
            if info['website']:
                contact_info += f"\n🌐 Site: {info['website']}"
            return f"Entre em contato conosco:\n\n{contact_info}\n\nPrefere agendar por WhatsApp para atendimento mais rápido!"
        
        elif intent == 'location':
            return f"📍 Estamos localizados em:\n{info['address']}\n\nFácil acesso e estacionamento próximo!"
        
        elif intent == 'booking':
            return f"Para agendar seu horário, entre em contato pelo WhatsApp: {info['whatsapp']} 📱\n\nNosso atendimento é rápido e personalizado!"
        
        elif intent == 'help':
            return "Posso te ajudar com:\n• Informações sobre serviços e preços\n• Horários de funcionamento\n• Localização do studio\n• Contato para agendamento\n\nO que você gostaria de saber? 😊"
        
        elif intent == 'date':
            days = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
            today = datetime.now()
            day_name = days[today.weekday()]
            return f"Hoje é {day_name}, {today.strftime('%d/%m/%Y')}. Confira nossos horários de funcionamento acima! Estamos prontas para te atender. 💅"
        
        # Check for specific service mention
        service = self._extract_service_from_message(user_message, info['services'])
        if service:
            if service.id in self.session_state['services_discussed']:
                return f"Já conversamos sobre {service.name}! 😊\nR$ {service.price:.2f} - {service.duration_minutes} minutos\n\nQuer agendar ou conhecer outro serviço?"
            else:
                self.session_state['services_discussed'].append(service.id)
                response = f"✨ {service.name} ✨\n💰 R$ {service.price:.2f}\n⏱️ Duração: {service.duration_minutes} minutos"
                if service.description:
                    response += f"\n\n{service.description}"
                response += f"\n\nPara agendar, chame no WhatsApp: {info['whatsapp']}"
                return response
        
        # For unknown intents, use AI if available
        if self.client and Config.AI_API_KEY != 'your-api-key-here':
            try:
                # Include conversation context
                context = "\n".join([f"User: {h['user']}" for h in self.session_state['conversation_history'][-3:]])
                
                response = self.client.chat.completions.create(
                    model=Config.AI_MODEL,
                    messages=[
                        {"role": "system", "content": self._generate_system_prompt(info)},
                        {"role": "user", "content": f"Contexto da conversa:\n{context}\n\nMensagem atual: {user_message}"}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"AI Error: {e}")
        
        # Final fallback
        return "Não entendi sua pergunta. 🤔 Posso te ajudar com:\n• Nossos serviços e preços\n• Horários de funcionamento\n• Agendamento via WhatsApp\n• Localização\n\nO que você gostaria de saber?"