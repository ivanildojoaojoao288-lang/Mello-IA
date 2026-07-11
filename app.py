from flask import Flask, render_template, request, jsonify
import os
import json
import hashlib
from datetime import datetime

app = Flask(__name__)

# Garantir que a pasta de logs existe
if not os.path.exists("storage"): os.makedirs("storage")

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message")
    user_id = hashlib.md5(request.remote_addr.encode()).hexdigest()
    
    # Lógica de processamento
    resposta = f"Comando '{user_msg}' processado pelo Core Mello IA."
    
    # Registo de auditoria
    with open(f"storage/log_{user_id}.jsonl", "a") as f:
        f.write(json.dumps({"ts": datetime.now().isoformat(), "msg": user_msg, "resp": resposta}) + "\n")
        
    return jsonify({"response": resposta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
