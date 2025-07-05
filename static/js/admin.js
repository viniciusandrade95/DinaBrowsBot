// Admin panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Business form submission
    document.getElementById('businessForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const data = {
            studio_name: document.getElementById('studio_name').value,
            address: document.getElementById('address').value,
            phone: document.getElementById('phone').value,
            whatsapp: document.getElementById('whatsapp').value,
            website: document.getElementById('website').value
        };
        
        try {
            const response = await fetch('/admin/update-business', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                showAlert('success', result.message);
            } else {
                showAlert('danger', result.message);
            }
        } catch (error) {
            showAlert('danger', 'Erro ao salvar informações');
        }
    });
    
    // Bot config form submission
    document.getElementById('botConfigForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const data = {
            bot_tone: document.getElementById('bot_tone').value,
            bot_intro_message: document.getElementById('bot_intro_message').value
        };
        
        try {
            const response = await fetch('/admin/update-business', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                showAlert('success', 'Configuração do bot atualizada!');
            }
        } catch (error) {
            showAlert('danger', 'Erro ao salvar configuração');
        }
    });
    
    // Hours form submission
    document.getElementById('hoursForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const hours = [];
        document.querySelectorAll('#hoursForm tbody tr').forEach((row, index) => {
            const hourId = row.querySelector('input[type="time"]').id.split('_')[1];
            hours.push({
                id: parseInt(hourId),
                open_time: document.getElementById(`open_${hourId}`).value,
                close_time: document.getElementById(`close_${hourId}`).value,
                is_closed: document.getElementById(`closed_${hourId}`).checked
            });
        });
        
        try {
            const response = await fetch('/admin/update-hours', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ hours })
            });
            
            const result = await response.json();
            if (result.success) {
                showAlert('success', result.message);
            }
        } catch (error) {
            showAlert('danger', 'Erro ao salvar horários');
        }
    });
    
    // Handle closed checkbox changes
    document.querySelectorAll('.closed-check').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const hourId = this.dataset.hourId;
            const openInput = document.getElementById(`open_${hourId}`);
            const closeInput = document.getElementById(`close_${hourId}`);
            
            if (this.checked) {
                openInput.disabled = true;
                closeInput.disabled = true;
            } else {
                openInput.disabled = false;
                closeInput.disabled = false;
            }
        });
    });
    
    // Add service
    document.getElementById('saveNewService').addEventListener('click', async function() {
        const data = {
            name: document.getElementById('serviceName').value,
            price: document.getElementById('servicePrice').value,
            duration: document.getElementById('serviceDuration').value,
            description: document.getElementById('serviceDescription').value
        };
        
        if (!data.name || !data.price || !data.duration) {
            showAlert('warning', 'Preencha todos os campos obrigatórios');
            return;
        }
        
        try {
            const response = await fetch('/admin/add-service', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                // Add service to table
                const tbody = document.getElementById('servicesTable');
                const row = tbody.insertRow();
                row.dataset.serviceId = result.service.id;
                row.innerHTML = `
                    <td>${result.service.name}</td>
                    <td>R$ ${result.service.price.toFixed(2)}</td>
                    <td>${result.service.duration_minutes} min</td>
                    <td>
                        <button class="btn btn-sm btn-warning edit-service" data-service-id="${result.service.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-service" data-service-id="${result.service.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                
                // Close modal and reset form
                bootstrap.Modal.getInstance(document.getElementById('addServiceModal')).hide();
                document.getElementById('addServiceForm').reset();
                showAlert('success', result.message);
                
                // Add event listeners to new buttons
                attachServiceButtonListeners();
            }
        } catch (error) {
            showAlert('danger', 'Erro ao adicionar serviço');
        }
    });
    
    // Delete service
    function attachServiceButtonListeners() {
        document.querySelectorAll('.delete-service').forEach(button => {
            button.addEventListener('click', async function() {
                if (!confirm('Tem certeza que deseja excluir este serviço?')) return;
                
                const serviceId = this.dataset.serviceId;
                
                try {
                    const response = await fetch(`/admin/delete-service/${serviceId}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        // Remove row from table
                        this.closest('tr').remove();
                        showAlert('success', result.message);
                    }
                } catch (error) {
                    showAlert('danger', 'Erro ao excluir serviço');
                }
            });
        });
    }
    
    // Attach listeners on page load
    attachServiceButtonListeners();
    
    // Chat test functionality
    let chatMessages = document.getElementById('chatMessages');
    let testMessage = document.getElementById('testMessage');
    let sendButton = document.getElementById('sendMessage');
    let resetButton = document.getElementById('resetChat');
    
    sendButton.addEventListener('click', sendTestMessage);
    testMessage.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendTestMessage();
    });
    
    resetButton.addEventListener('click', async function() {
        try {
            await fetch('/bot/reset', { method: 'POST' });
            chatMessages.innerHTML = '<div class="text-muted">Chat resetado. Envie uma mensagem para começar...</div>';
        } catch (error) {
            console.error('Error resetting chat:', error);
        }
    });
    
    async function sendTestMessage() {
        const message = testMessage.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat(message, 'user');
        testMessage.value = '';
        
        try {
            const response = await fetch('/bot/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
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
        if (chatMessages.querySelector('.text-muted')) {
            chatMessages.innerHTML = '';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Alert helper
    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});