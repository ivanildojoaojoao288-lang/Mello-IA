import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")

print("CHAVE CARREGADA:", bool(API_KEY))
print("MODELO:", MODEL)

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna.

Características:

- Respostas claras e profissionais.
- Linguagem simples.
- Ajuda em programação, tecnologia, estudos e informação geral.
- Nunca reveles chaves ou configurações internas.

Quando perguntarem:
"Quem criou a Mello IA?"

Responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João Paulo Augusto,
com foco em inteligência artificial, programação e inovação tecnológica."
"""


@app.route("/")
def inicio():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():

    dados = request.get_json(silent=True) or {}

    mensagem = dados.get("message", "").strip()

    if not mensagem:
        return jsonify({
            "reply": "Por favor escreva uma mensagem."
        }), 400

    if not API_KEY:
        return jsonify({
            "reply": "A chave da API não está configurada no servidor."
        }), 500

    if not MODEL:
        return jsonify({
            "reply": "O modelo da IA não está configurado no servidor."
        }), 500

    try:

        resposta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": MODEL,

                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": mensagem
                    }
                ],

                "temperature": 0.7
            },

            timeout=60
        )

        resultado = resposta.json()

        print("RESPOSTA OPENROUTER:")
        print(resultado)

        if "choices" not in resultado:

            return jsonify({
                "reply": "Erro na comunicação com a IA.",
                "detalhes": resultado
            }), 500

        texto = resultado["choices"][0]["message"]["content"]

        return jsonify({
            "reply": texto
        })

    except Exception as erro:

        print("ERRO:", erro)

        return jsonify({
            "reply": "Erro interno da Mello IA.",
            "detalhes": str(erro)
        }), 500


if __name__ == "__main__":

    print("🚀 Mello IA online")

    app.run(
        host="0.0.0.0",
        port=5000
    )
    
