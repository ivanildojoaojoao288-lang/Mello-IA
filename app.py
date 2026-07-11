"""
Mello IA Core Engine v5.0
Eng. Ivanildo | 2026
Arquitetura de alta robustez e persistência.
"""

import logging
import json
import os
import time
import requests
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# --- Configuração de Log de Nível Industrial ---
logging.basicConfig(
    filename='mello_engine.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

app = Flask(__name__)

# --- Motor de Persistência de Contexto (Simulação de Base de Dados local) ---
class SystemMemory:
    def __init__(self):
        self.context_path = "storage/context.json"
        if not os.path.exists("storage"): os.makedirs("storage")
        
    def save_log(self, user_id, message, response):
        """Grava cada transação num log estruturado para auditoria."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_id,
            "query": message,
            "response": response
        }
        with open(f"storage/log_{user_id}.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

# --- Motor de Processamento de IA (Classe de Alto Nível) ---
class MelloIAEngine:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.history = {}

    def get_context(self, user_id):
        return self.history.get(user_id, [])

    def update_context(self, user_id, user_input, ai_output):
        if user_id not in self.history: self.history[user_id] = []
        self.history[user_id].append({"role": "user", "content": user_input})
        self.history[user_id].append({"role": "assistant", "content": ai_output})
        
        # Limitar histórico para não sobrecarregar a memória
        if len(self.history[user_id]) > 20: self.history[user_id] = self.history[user_id][-20:]

    def execute(self, user_id, message):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": [{"role": "system", "content": "Sistema operativo de IA: Mello. Foco: Solução técnica de redes e sistemas."}] + self.get_context(user_id) + [{"role": "user", "content": message}],
            "temperature": 0.1
        }
        response = requests.post(self.url, headers=headers, json=payload, timeout=30)
        return response.json()['choices'][0]['message']['content']

# Inicialização da Engine
engine = MelloIAEngine(api_key="sk-or-v1-COLA_AQUI_A_TUA_CHAVE_REAL")
memory = SystemMemory()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = hashlib.md5(request.remote_addr.encode()).hexdigest()
    user_msg = data.get("message")
    
    try:
        response = engine.execute(user_id, user_msg)
        engine.update_context(user_id, user_msg, response)
        memory.save_log(user_id, user_msg, response)
        return jsonify({"response": response})
    except Exception as e:
        logging.error(f"Falha na execução: {e}")
        return jsonify({"response": "SYSTEM_CRITICAL_FAILURE: Contactar Eng. Ivanildo."}), 500

if __name__ == '__main__':
    # Configurações de servidor de produção
    app.run(host='0.0.0.0', port=5000, debug=False)
