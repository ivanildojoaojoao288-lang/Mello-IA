from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuração de ambiente segura
API_KEY = "sk-or-v1-COLA_AQUI_A_TUA_CHAVE_REAL"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get("message")
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [
            {"role": "system", "content": "Tu és a Mello IA, um assistente técnico de alto nível. Responde sempre em Português (Moçambique), de forma direta, técnica e profissional. Sê conciso."},
            {"role": "user", "content": user_msg}
        ]
    }
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content']
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"response": "Erro técnico no processamento da solicitação."}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
