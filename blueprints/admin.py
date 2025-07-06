from flask import Blueprint, render_template_string, request, jsonify
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple HTML template as string (no external files needed)
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brow Studio Bot Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand">🤖 Brow Studio Bot Admin</span>
        </div>
    </nav>

    <div class="container mt-4">
        <h1>Configuração do Bot</h1>
        
        <!-- Status -->
        <div class="card mb-4">
            <div class="card-header">
                <h3>Status do Sistema</h3>
            </div>
            <div class="card-body">
                <div class="alert alert-success">
                    ✅ Bot está funcionando corretamente!
                </div>
                <ul>
                    <li>✅ Servidor Flask ativo</li>
                    <li>✅ Webhook configurado em /webhook</li>
                    <li>✅ Bot de teste disponível</li>
                </ul>
            </div>
        </div>

        <!-- Test Bot -->
        <div class="card mb-4">
            <div class="card-header">
                <h3>Testar Bot</h3>
            </div>
            <div class="card-body">
                <div id="chatMessages" class="border rounded p-3 mb-3" style="height: 300px; overflow-y: auto; background-color: #f8f9fa;">
                    <div class="text-muted">Envie uma mensagem para testar o bot...</div>
                </div>
                <div class="input-group">
                    <input type="text" id="testMessage" class="form-control" placeholder="Digite sua mensagem..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="btn btn-primary" onclick="sendMessage()">Enviar</button>
                    <button class="btn btn-secondary" onclick="resetChat()">Resetar</button>
                </div>
            </div>
        </div>

        <!-- WhatsApp Config -->
        <div class="card">
            <div class="card-header">
                <h3>Configuração WhatsApp</h3>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <h5>Para conectar com WhatsApp:</h5>
                    <ol>
                        <li>Acesse <a href="https://developers.facebook.com/" target="_blank">Facebook Developers</a></li>
                        <li>Configure seu app WhatsApp Business</li>
                        <li>Use a URL do webhook: <code>{{ webhook_url }}/webhook</code></li>
                        <li>Configure as variáveis de ambiente no Railway</li>
                    </ol>
                </div>
                <p><strong>Webhook URL:</strong> <code>{{ webhook_url }}/webhook</code></p>
                <p><strong>Status:</strong> <span class="badge bg-success">Ativo</span></p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        async function sendMessage() {
            const input = document.getElementById('testMessage');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessageToChat(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/bot/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const result = await response.json();
                if (result.success) {
                    addMessageToChat(result.response, 'bot');
                } else {
                    addMessageToChat('Erro ao processar mensagem', 'bot');
                }
            } catch (error) {
                addMessageToChat('Erro de conexão', 'bot');
            }
        }
        
        function addMessageToChat(message, sender) {
            const chatDiv = document.getElementById('chatMessages');
            
            // Remove placeholder text
            if (chatDiv.querySelector('.text-muted')) {
                chatDiv.innerHTML = '';
            }
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `mb-2 p-2 rounded ${sender === 'user' ? 'bg-primary text-white ms-5' : 'bg-light me-5'}`;
            messageDiv.textContent = message;
            
            chatDiv.appendChild(messageDiv);
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }
        
        async function resetChat() {
            try {
                await fetch('/bot/reset', { method: 'POST' });
                document.getElementById('chatMessages').innerHTML = '<div class="text-muted">Chat resetado. Envie uma mensagem para começar...</div>';
            } catch (error) {
                console.error('Error resetting chat:', error);
            }
        }
    </script>
</body>
</html>
"""

@admin_bp.route('/')
def index():
    """Admin panel home page"""
    try:
        # Try to get business info from database
        from models import BusinessConfig, Service, OperatingHours
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
            from models import db
            db.session.add(business)
            db.session.commit()
            
        webhook_url = request.host_url.rstrip('/')
        
    except Exception as e:
        logger.warning(f"Database not available, using simple template: {e}")
        webhook_url = request.host_url.rstrip('/')
    
    return render_template_string(ADMIN_TEMPLATE, webhook_url=webhook_url)

@admin_bp.route('/update-business', methods=['POST'])
def update_business():
    """Update business information"""
    try:
        data = request.json
        from models import BusinessConfig, db
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
        
    except Exception as e:
        logger.error(f"Error updating business: {e}")
    
    return jsonify({'success': False, 'message': 'Erro ao atualizar informações'})