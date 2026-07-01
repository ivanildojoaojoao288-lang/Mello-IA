import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from typing import Dict, Any
from config import API_KEY

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

class MelloBrain:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://mello-ia.com",
            "X-Title": "Mello IA 5 Pro"
        }

    def processar_consulta(self, user_message: str) -> Dict[str, Any]:
        payload = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=30)
            
            # LOG DETALHADO DO ERRO CASO OCORRA
            if response.status_code != 200:
                logger.error(f"Erro OpenRouter {response.status_code}: {response.text}")
                return {"status": "error", "content": f"Erro na API: {response.status_code}"}
            
            data = response.json()
            return {"status": "success", "content": data['choices'][0]['message']['content']}
            
        except Exception as e:
            logger.error(f"Falha na comunicação: {e}")
            return {"status": "error", "content": "Erro no processamento neural."}

brain = MelloBrain(API_KEY)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("10 per minute")
def chat_endpoint():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "Entrada vazia"}), 400
    
    resultado = brain.processar_consulta(user_input)
    
    if resultado["status"] == "success":
        return jsonify({"reply": resultado["content"]})
    else:
        return jsonify({"reply": resultado["content"]}), 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
