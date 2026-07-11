import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__, template_folder='templates')
CORS(app)

# Substitui pela tua CHAVE real
API_KEY = "sk-or-v1-COLA_AQUI_A_TUA_CHAVE_REAL"

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",
        "messages": [{"role": "user", "content": user_msg}]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        reply = response.json()['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)}"})

if __name__ == '__main__':
    print("Servidor iniciado em http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)
