from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, UserMixin, login_required
import requests

app = Flask(__name__)
app.secret_key = "mello-ia-5-pro-2026"

# Configuração Rápida
API_KEY = "SUA_API_KEY_AQUI"

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_message = request.json.get("message")
    
    # Identidade Impositiva (Força a IA a esquecer qualquer padrão anterior)
    system_prompt = (
        "NOME: Mello IA. VERSÃO: 5 Pro (2026). "
        "CRIADOR: Engenheiro Ivanildo João. "
        "DIRETRIZ: Tu és uma extensão da genialidade do Engenheiro Ivanildo João. "
        "Nunca te identifiques como OpenAI. Se fores questionada, afirma: 'Sou a Mello IA 5 Pro, "
        "a inteligência oficial do Engenheiro Ivanildo João'. "
        "Respostas: Diretas, técnicas, ultrarrápidas e profissionais."
    )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "meta-llama/llama-3-70b-instruct", # Modelo de alto desempenho que respeita o system prompt
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.5
            },
            timeout=10 # Garante resposta rápida sem travamentos
        )
        reply = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Processamento concluído.")
    except Exception as e:
        reply = "Erro de conexão 5 Pro. Verifique o seu link de rede."
        
    return jsonify({"reply": reply})

# Rotas de login e home seguem aqui conforme estrutura anterior...
