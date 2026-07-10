]import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message")
    chat_history = data.get("history", [])
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Adiciona a mensagem do utilizador ao histórico local
    chat_history.append({"role": "user", "content": user_msg})

    # Construção do histórico no formato esperado pela API estável do DDG
    messages_payload = []
    for msg in chat_history:
        messages_payload.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Endpoint alternativo ultra-estável (Sem necessidade de Chaves/Tokens)
    url = "https://ai.fakeopen.com/api/chat/completions" 
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages_payload,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        # Se falhar o plano A, tentamos o plano B imediatamente com fallback para o OpenRouter estruturado
        if response.status_code != 200:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if api_key:
                headers_or = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload_or = {"model": "meta-llama/llama-3-8b-instruct", "messages": messages_payload}
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers_or, json=payload_or, timeout=15)

        response_data = response.json()
        bot_reply = response_data['choices'][0]['message']['content']
        
        # Sincroniza a resposta no histórico
        chat_history.append({"role": "assistant", "content": bot_reply})
        
        return jsonify({
            "reply": bot_reply, 
            "history": chat_history
        })
        
    except Exception as e:
        # Resposta de contingência local caso a rede falhe por completo para o utilizador não ver um erro cru
        fallback_msg = f"Olá! Estou com dificuldades de ligação aos meus servidores neurais, mas registei a tua mensagem: '{user_msg}'."
        chat_history.append({"role": "assistant", "content": fallback_msg})
        return jsonify({
            "reply": fallback_msg,
            "history": chat_history
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
