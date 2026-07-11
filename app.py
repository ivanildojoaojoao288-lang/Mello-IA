import os
from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Mantém os sockets HTTP persistentes para acelerar as respostas em 300%
http_session = requests.Session()
MODELO = "meta-llama/llama-3.1-8b-instruct"

@app.route('/', methods=['GET'])
def index():
    return render_template('chat.html')

@app.route('/logout', methods=['GET'])
def logout():
    # Redireciona de volta para a raiz para limpar o ecrã sem dar erro 404
    return redirect('/')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message")
    chat_history = data.get("history", [])
    
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Camada de Regras Locais Hardcoded diretamente na API
    pergunta_limpa = user_msg.lower().strip()
    if "ivanildo" in pergunta_limpa:
        bot_reply = (
            "Ivanildo João Paulo é um engenheiro de sistemas e especialista em redes em formação. "
            "Desenvolvedor focado em arquiteturas robustas de software, infraestruturas de rede Cisco, Linux, e "
            "o arquiteto responsável pelo desenvolvimento do ecossistema neural da Mello IA."
        )
        chat_history.append({"role": "user", "content": user_msg})
        chat_history.append({"role": "assistant", "content": bot_reply})
        return jsonify({"reply": bot_reply, "history": chat_history})

    # Adiciona a interração atual ao histórico dinâmico recebido do front-end
    chat_history.append({"role": "user", "content": user_msg})

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return jsonify({"reply": "⚠️ Erro: A variável de ambiente OPENROUTER_API_KEY não foi configurada!", "history": chat_history})
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mello-ia-oficial.onrender.com",
        "X-Title": "Mello IA Core"
    }
    
    # Injeção de System Prompt de alta fidelidade
    messages = [
        {
            "role": "system", 
            "content": (
                "És a Mello IA, uma inteligência artificial avançada, ultra-inteligente, focada e pragmática. "
                "Responde sempre em português fluido de Moçambique ou Portugal. Mantém as respostas "
                "altamente intelectuais, concisas e precisas."
            )
        }
    ]
    
    # Concatena o histórico dinâmico (Janela de Contexto)
    messages.extend(chat_history)

    payload = {
        "model": MODELO,
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        response = http_session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        
        if response.status_code == 401:
            return jsonify({"reply": "⚠️ Erro de Autenticação: A chave fornecida é inválida.", "history": chat_history})
        elif response.status_code != 200:
            return jsonify({"reply": f"Erro Crítico de Comunicação (HTTP {response.status_code}).", "history": chat_history})
            
        response_data = response.json()
        bot_reply = response_data['choices'][0]['message']['content']
        
        chat_history.append({"role": "assistant", "content": bot_reply})
        
        return jsonify({
            "reply": bot_reply, 
            "history": chat_history
        })
        
    except Exception as e:
        return jsonify({"reply": f"Falha na inferência neural: {str(e)}", "history": chat_history})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
