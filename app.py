import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 🌐 ROTA PRINCIPAL: Serve a tua interface HTML
@app.route('/', methods=['GET'])
def index():
    return render_template('chat.html')

# 🧠 ROTA DE PROCESSAMENTO: Comunicação direta com o OpenRouter
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message")
    
    # Recebe o histórico vindo do navegador para manter o contexto da conversa
    chat_history = data.get("history", [])
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Adiciona a mensagem do utilizador ao fluxo
    chat_history.append({"role": "user", "content": user_msg})

    # Puxa a chave configurada no painel do Render
    api_key = os.getenv('OPENROUTER_API_KEY')
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    # Payload ajustado com o modelo Llama 3.1 Gratuito ativo
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": chat_history,
        "max_tokens": 500
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        # Proteção caso a API do OpenRouter devolva alguma estrutura inesperada
        if "choices" not in response_data:
            return jsonify({"error": "Erro na API externa", "details": response_data}), 502
            
        bot_reply = response_data['choices'][0]['message']['content']
        
        # Adiciona a resposta da IA ao histórico que vai voltar para o cliente
        chat_history.append({"role": "assistant", "content": bot_reply})
        
        return jsonify({
            "reply": bot_reply, 
            "history": chat_history
        })
        
    except Exception as e:
        return jsonify({"error": "Falha na comunicação neural", "details": str(e)}), 503

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
