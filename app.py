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

    dados = request.json

    mensagem = dados.get("message", "")
    historico = dados.get("history", [])

    if not mensagem:
        return jsonify({
            "reply": "Por favor escreva uma mensagem."
        })


    historico.append({
        "role": "user",
        "content": mensagem
    })


    resposta = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages":[
                {
                    "role":"system",
                    "content":SYSTEM_PROMPT
                }
            ] + historico,
            "temperature":0.7,
            "max_tokens":1000
        },
        timeout=60
    )


    resultado = resposta.json()

    texto = resultado["choices"][0]["message"]["content"]


    return jsonify({
        "reply":texto
    })



if __name__ == "__main__":
    print("🚀 Mello IA online")
    app.run(
        host="0.0.0.0",
        port=5000
    )
