import os
import requests
from flask import Flask, request, jsonify, render\_template
from flask\_cors import CORS
from dotenv import load\_dotenv

load\_dotenv()

app = Flask(**name**)
CORS(app)

API\_KEY = os.getenv("OPENROUTER\_API\_KEY")
MODEL = os.getenv("OPENROUTER\_MODEL")

print("CHAVE CARREGADA:", bool(API\_KEY))
print("MODELO:", MODEL)

SYSTEM\_PROMPT = """
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
return render\_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():

```
dados = request.get_json(silent=True) or {}

mensagem = dados.get("message", "").strip()


if not mensagem:
    return jsonify({
        "reply": "Por favor escreva uma mensagem."
    }), 400


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

    return jsonify({

        "reply": "Erro interno da Mello IA.",

        "detalhes": str(erro)

    }), 500
```



if **name** == "**main**":

```
print("🚀 Mello IA online")

app.run(
    host="0.0.0.0",
    port=5000
)
```
