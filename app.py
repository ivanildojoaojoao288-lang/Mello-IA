import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# CHAVE INJETADA PARA TESTE LOCAL (Substitui pela tua chave real)
API_KEY = "sk-or-v1-COLA_AQUI_A_TUA_CHAVE_REAL"

@app.route('/', methods=['GET'])
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message")
    chat_history = data.get("history", [])

    if not user_msg:
        return jsonify({"reply": "Erro: Mensagem vazia", "history": chat_history})

    # Regra fixa
    if "ivanildo" in user_msg.lower():
        bot_reply = "Ivanildo João Paulo é o arquiteto da Mello IA e engenheiro de redes."
        chat_history.append({"role": "user", "content": user_msg})
        chat_history.append({"role": "assistant", "content": bot_reply})
        return jsonify({"reply": bot_reply, "history": chat_history})

    chat_history.append({"role": "user", "content": user_msg})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mello-ia-oficial.onrender.com",
        "X-Title": "Mello IA Core"
    }

    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [{"role": "system", "content": "És a Mello IA, concisa e precisa."}] + chat_history,
        "max_tokens": 500
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        response.raise_for_status() # Verifica erros HTTP
        bot_reply = response.json()['choices'][0]['message']['content']
        chat_history.append({"role": "assistant", "content": bot_reply})
        return jsonify({"reply": bot_reply, "history": chat_history})
    except Exception as e:
        return jsonify({"reply": f"Erro de conexão: {str(e)}", "history": chat_history})

if __name__ == '__main__':
    print("Servidor a arrancar... Acede a http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)
