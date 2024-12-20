import os
from flask import Flask, render_template, request, jsonify
from src.models.chat_with_improved_rick import ImprovedRickBot
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Make rickbot a global variable
rickbot = None

def initialize_rickbot():
    global rickbot
    try:
        model_path = os.getenv('MODEL_PATH', 'models/rickbot-improved')
        rickbot = ImprovedRickBot(model_path=model_path)
        logger.info("RickBot initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing RickBot: {str(e)}")
        return str(e)

# Initialize RickBot when app starts
initialize_rickbot()

@app.route('/healthz')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global rickbot
    try:
        # Check if RickBot is initialized
        if rickbot is None:
            error = initialize_rickbot()
            if error:
                return jsonify({
                    'response': f"*burp* Error initializing RickBot: {error}"
                }), 500

        user_message = request.json['message'].strip()
        
        # Handle special commands
        if user_message.lower() == 'quit':
            return jsonify({'command': 'quit'})
        elif user_message.lower() == 'clear':
            return jsonify({'command': 'clear'})
            
        # Handle empty messages
        if not user_message:
            return jsonify({'response': '*burp* Say something, Morty!'})
            
        # Handle science questions
        if user_message.lower().startswith('science'):
            response = rickbot.get_scientific_response(user_message[7:].strip())
        else:
            response = rickbot.generate_response(user_message)
            
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return jsonify({
            'response': "*burp* Something went wrong in dimension C-137!"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)