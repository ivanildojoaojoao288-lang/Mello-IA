import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Mello IA 5 Pro Online", 
        "versao": "5.0.0", 
        "engine": "Production"
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message")
    
    # 🧠 Recebe o histórico que vem do Front-end (se não vier, começa um novo)
    chat_history = data.get("history", [])
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Adiciona a nova mensagem do utilizador ao fluxo atual
    chat_history.append({"role": "user", "content": user_msg})

    # Chamada otimizada para OpenRouter
    api_key = os.getenv('OPENROUTER_API_KEY')
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": chat_history,  # Passa o histórico isolado deste utilizador
        "max_tokens": 500
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        # Proteção caso a API do OpenRouter devolva algum erro de cota/chave
        if "choices" not in response_data:
            return jsonify({"error": "Erro na API externa", "details": response_data}), 502
            
        bot_reply = response_data['choices'][0]['message']['content']
        
        # Adiciona a resposta do assistente ao histórico que vai voltar para o cliente
        chat_history.append({"role": "assistant", "content": bot_reply})
        
        # Devolve a resposta e o histórico atualizado para o front-end guardar
        return jsonify({
            "reply": bot_reply, 
            "history": chat_history
        })
        
    except Exception as e:
        return jsonify({"error": "Falha na comunicação neural", "details": str(e)}), 503

if __name__ == '__main__':
    # O Render configura a porta automaticamente pela variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
