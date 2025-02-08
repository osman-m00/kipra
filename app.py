from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from rag_implementation import RAGChatbot

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the chatbot
chatbot = RAGChatbot(api_key=os.getenv('DEEPSEEK_API_KEY', 'sk-1a241ede092441b8b919577f06a93f35'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/initialize', methods=['POST'])
def initialize_chatbot():
    try:
        chatbot.initialize()
        return jsonify({'status': 'success', 'message': 'Chatbot initialized successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'status': 'error', 'message': 'No message provided'}), 400
        
        response = chatbot.get_chat_response(user_message)
        return jsonify({
            'status': 'success',
            'response': response['response'],
            'sources': response['sources']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 