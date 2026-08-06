import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurações
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "")

if not API_KEY:
    raise RuntimeError("A variável OPENROUTER_API_KEY não foi configurada.")

SYSTEM_PROMPT = """
És um assistente inteligente, profissional e preciso.

Regras:
- Responde sempre de forma clara.
- Não inventes informações.
- Quando não souberes uma resposta, admite isso.
- Nunca reveles informações internas do sistema.
- Nunca reveles variáveis de ambiente.
- Nunca reveles chaves secretas.

Se alguém perguntar:

"Quem desenvolveu esta aplicação?"

Responde:

"Esta aplicação foi desenvolvida pelo Eng. Ivanildo João Paulo Augusto."
"""

@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "online"
    })


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({
            "reply": "Escreva uma mensagem.",
            "history": history
        }), 400

    history.append({
        "role": "user",
        "content": message
    })

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + history
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()

        answer = response.json()["choices"][0]["message"]["content"]

        history.append({
            "role": "assistant",
            "content": answer
        })

        return jsonify({
            "reply": answer,
            "history": history
        })

    except requests.exceptions.HTTPError:
        return jsonify({
            "reply": response.text,
            "history": history
        }), response.status_code

    except Exception as e:
        return jsonify({
            "reply": str(e),
            "history": history
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
