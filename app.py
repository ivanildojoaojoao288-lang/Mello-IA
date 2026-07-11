from flask import Flask, render_template, request, jsonify
import logging
import json
import os
import hashlib
from datetime import datetime

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)

# --- Motor de Persistência ---
class SystemMemory:
    def __init__(self):
        if not os.path.exists("storage"): os.makedirs("storage")
        
    def save_log(self, user_id, message, response):
        log_entry = {"timestamp": datetime.now().isoformat(), "query": message, "response": response}
        with open(f"storage/log_{user_id}.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

memory = SystemMemory()

# --- Rotas Principais ---
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get("message")
    user_id = hashlib.md5(request.remote_addr.encode()).hexdigest()
    
    # Simulação da resposta da IA (Substitui pela chamada real à API se já tiveres)
    resposta = f"Sistema operacional Mello IA: Comando '{user_msg}' processado com sucesso."
    
    memory.save_log(user_id, user_msg, resposta)
    return jsonify({"response": resposta})

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
