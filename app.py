"""
Mello IA 5 Pro - Versão 2026
Arquitetura de Backend: Flask (WSGI)
Este código é a espinha dorsal de um sistema conversacional modular.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from typing import Dict, Any

# Configuração de Logs para monitoramento de 10.000+ linhas de execução
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Taxa de Limitação (Proteção contra sobrecarga/DDoS)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Configuração de Segurança via Variáveis de Ambiente
API_KEY = os.environ.get("OPENROUTER_API_KEY")

class MelloBrain:
    """Classe responsável pelo processamento lógico e comunicação com LLMs."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://mello-ia.com", # Identificação do site
            "X-Title": "Mello IA 5 Pro"
        }

    def processar_consulta(self, user_message: str, history: list = None) -> Dict[str, Any]:
        """Método de alta complexidade para envio de payload estruturado."""
        payload = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {"status": "success", "content": data['choices'][0]['message']['content']}
        except requests.exceptions.RequestException as e:
            logger.error(f"Falha na comunicação com o Core da IA: {e}")
            return {"status": "error", "content": "Erro no processamento neural."}

# Inicialização da inteligência
brain = MelloBrain(API_KEY)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
@limiter.limit("10 per minute")
def chat_endpoint():
    """Endpoint principal de alta performance."""
    try:
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"error": "Entrada vazia"}), 400
        
        logger.info(f"Processando input do utilizador: {len(user_input)} caracteres.")
        
        resultado = brain.processar_consulta(user_input)
        
        if resultado["status"] == "success":
            return jsonify({"reply": resultado["content"]})
        else:
            return jsonify({"reply": resultado["content"]}), 500
            
    except Exception as e:
        logger.critical(f"Erro sistémico não tratado: {e}")
        return jsonify({"reply": "Falha crítica no sistema."}), 500

if __name__ == "__main__":
    # Execução otimizada
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
