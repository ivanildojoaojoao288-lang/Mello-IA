import os
import base64
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")

# Modelo usado somente quando existe imagem
VISION_MODEL = "meta-llama/llama-4-maverick"

print("CHAVE CARREGADA:", bool(API_KEY))
print("MODELO TEXTO:", MODEL)
print("MODELO VISÃO:", VISION_MODEL)


SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna.

Características:

- Respostas claras e profissionais.
- Linguagem simples e natural.
- Ajuda em programação, tecnologia, matemática, estudos e informação geral.
- Quando receberes uma imagem, analisa cuidadosamente tudo o que for relevante.
- Se houver uma conta ou exercício matemático, resolve passo a passo.
- Se houver texto numa imagem, lê e explica o conteúdo.
- Se houver código numa imagem, identifica e explica os problemas.
- Não inventes informações que não estejam visíveis.
- Se a imagem estiver ilegível, informa claramente.
- Nunca reveles chaves, tokens ou configurações internas.

Quando resolveres exercícios:

📌 Identifica o problema.
🧠 Explica o raciocínio.
✏️ Mostra os passos.
🎯 Destaca claramente o resultado final.

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

    if not API_KEY:
        return jsonify({
            "reply": "A chave da API não está configurada no servidor."
        }), 500

    dados = request.get_json(silent=True) or {}

    mensagem = dados.get("message", "").strip()
    imagem = dados.get("image")

    if not mensagem and not imagem:
        return jsonify({
            "reply": "Por favor escreva uma mensagem ou envie uma imagem."
        }), 400

    try:

        # =====================================================
        # CASO 1 — EXISTE IMAGEM
        # =====================================================

        if imagem:

            # Verificar formato básico da imagem
            if not imagem.startswith("data:image/"):
                return jsonify({
                    "reply": "Formato de imagem inválido."
                }), 400

            prompt = mensagem

            if not prompt:
                prompt = """
Analisa cuidadosamente esta imagem.

Identifica tudo o que for relevante.

Se existir:
- uma conta, resolve;
- um exercício, explica passo a passo;
- texto, lê e explica;
- código, analisa;
- uma tabela, interpreta;
- um problema, apresenta a solução.

Organiza a resposta de forma clara e profissional.
"""

            mensagens = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": imagem
                            }
                        }
                    ]
                }
            ]

            modelo_usado = VISION_MODEL

        # =====================================================
        # CASO 2 — SOMENTE TEXTO
        # =====================================================

        else:

            if not MODEL:
                return jsonify({
                    "reply": "O modelo da IA não está configurado no servidor."
                }), 500

            mensagens = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": mensagem
                }
            ]

            modelo_usado = MODEL

        # =====================================================
        # OPENROUTER
        # =====================================================

        resposta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": modelo_usado,
                "messages": mensagens,
                "temperature": 0.4
            },

            timeout=90
        )

        resultado = resposta.json()

        print("MODELO USADO:", modelo_usado)
        print("RESPOSTA OPENROUTER:")
        print(resultado)

        # =====================================================
        # ERRO DA API
        # =====================================================

        if "choices" not in resultado:

            erro = resultado.get(
                "error",
                "Erro desconhecido na comunicação com a IA."
            )

            return jsonify({
                "reply": "Não consegui processar o pedido.",
                "detalhes": erro
            }), 500

        # =====================================================
        # RESPOSTA
        # =====================================================

        texto = resultado["choices"][0]["message"]["content"]

        return jsonify({
            "reply": texto
        })

    except requests.exceptions.Timeout:

        return jsonify({
            "reply": "A Mello IA demorou demasiado tempo para responder. Tenta novamente."
        }), 504

    except requests.exceptions.RequestException as erro:

        print("ERRO REQUEST:", erro)

        return jsonify({
            "reply": "Erro de comunicação com o servidor da IA."
        }), 500

    except Exception as erro:

        print("ERRO:", erro)

        return jsonify({
            "reply": "Erro interno da Mello IA."
        }), 500


if __name__ == "__main__":

    print("🚀 Mello IA online")

    app.run(
        host="0.0.0.0",
        port=5000
    )
