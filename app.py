import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 🌐 ROTA PRINCIPAL: Serve o Front-end
@app.route('/', methods=['GET'])
def index():
    return render_template('chat.html')

# 🧠 ROTA DE PROCESSAMENTO: Comunicação com OpenRouter + Logs Estratégicos
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message")
    
    # Recebe o histórico que vem do Front-end
    chat_history = data.get("history", [])
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Adiciona a nova mensagem do utilizador ao fluxo
    chat_history.append({"role": "user", "content": user_msg})

    api_key = os.getenv('OPENROUTER_API_KEY')
    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    # 🔄 Trocamos para o modelo gratuito para testar se o problema era cota/créditos
    payload = {
        "model": "google/gemma-2-9b-it:free",
        "messages": chat_history,
        "max_tokens": 500
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        
        # 🚨 ESTAS LINHAS VÃO IMPRIMIR O MOTIVO EXATO DO ERRO NOS LOGS DO RENDER
        print("--- DEBUG OPENROUTER ---")
        print("STATUS CODE:", response.status_code)
        print("RESPOSTA COMPLETA:", response.text)
        print("------------------------")
        
        response_data = response.json()
        
        # Proteção caso a API do OpenRouter devolva erro
        if "choices" not in response_data:
            return jsonify({"error": "Erro na API externa", "details": response_data}), 502
            
        bot_reply = response_data['choices'][0]['message']['content']
        
        # Adiciona a resposta da IA ao histórico
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
