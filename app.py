import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Permite que qualquer front-end conecte na sua API

# Histórico simulado (Em produção, use Redis ou Banco de Dados)
historico = []

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "Mello IA 5 Pro Online", "versao": "5.0.0", "engine": "Production"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get("message")
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Adiciona ao histórico (Memória)
    historico.append({"role": "user", "content": user_msg})

    # Chamada otimizada para OpenRouter
    headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": historico,
        "max_tokens": 500
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        bot_reply = response.json()['choices'][0]['message']['content']
        
        # Salva resposta no histórico
        historico.append({"role": "assistant", "content": bot_reply})
        
        return jsonify({"reply": bot_reply, "history_size": len(historico)})
    except Exception as e:
        return jsonify({"error": "Falha na comunicação neural", "details": str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
