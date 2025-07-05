from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>WhatsApp Bot is Running! 🎉</h1>
    <p>Webhook URL: /webhook</p>
    <p>Health Check: /health</p>
    '''

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == 'token123':
        return challenge
    return 'Invalid token', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    # This is for Railway
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
