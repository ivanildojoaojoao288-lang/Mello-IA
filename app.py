from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# A tua chave real aqui
API_KEY = "sk-or-v1-COLA_AQUI_A_TUA_CHAVE_REAL"

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get("message")
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [{"role": "user", "content": user_msg}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return jsonify({"reply": response.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"reply": "Erro no processamento: " + str(e)})

if __name__ == '__main__':
    # Usar debug=False para evitar conflitos de recarregamento se o microfone estiver a bloquear a porta
    app.run(host='127.0.0.1', port=5000, debug=False)
