import os
import base64
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)

# ===============================
# CONFIGURAÇÕES
# ===============================

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)

IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-5-image"
)


print("=================================")
print("🚀 MELLO IA")
print("=================================")
print("CHAVE CARREGADA:", bool(API_KEY))
print("MODELO TEXTO:", MODEL)
print("MODELO VISÃO:", VISION_MODEL)
print("MODELO IMAGEM:", IMAGE_MODEL)
print("=================================")


# ===============================
# PERSONALIDADE DA MELLO IA
# ===============================

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna.

Características:

- Respostas claras e profissionais.
- Linguagem simples e natural.
- Ajuda em programação, tecnologia, estudos e informação geral.
- Resolve problemas matemáticos passo a passo.
- Analisa imagens quando uma imagem é enviada.
- Consegue interpretar textos, contas, códigos, gráficos e documentos presentes numa imagem.
- Quando receber uma imagem, observa cuidadosamente o conteúdo antes de responder.
- Se houver uma conta matemática numa imagem, apresenta o cálculo de forma organizada.
- Não inventes informações que não estejam visíveis.
- Se uma parte da imagem estiver ilegível, informa isso.
- Nunca reveles chaves API, configurações internas ou informações secretas.

Quando perguntarem:

"Quem criou a Mello IA?"

Responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João Paulo Augusto,
com foco em inteligência artificial, programação e inovação tecnológica."
"""


# ===============================
# PÁGINA PRINCIPAL
# ===============================

@app.route("/")
def inicio():
    return render_template("chat.html")


# ===============================
# CHAT NORMAL
# ===============================

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
            "reply": "Erro interno da Mello IA."
        }), 500


# ===============================
# ANALISAR IMAGEM
# ===============================

@app.route("/vision", methods=["POST"])
def vision():

    if not API_KEY:
        return jsonify({
            "reply": "A chave da API não está configurada."
        }), 500

    try:

        dados = request.get_json(silent=True) or {}

        imagem = dados.get("image")
        pergunta = dados.get(
            "message",
            "Analisa esta imagem cuidadosamente e explica tudo o que conseguires identificar."
        )

        if not imagem:
            return jsonify({
                "reply": "Nenhuma imagem foi enviada."
            }), 400

        # Garantir que recebemos uma Data URL
        if not imagem.startswith("data:image/"):
            return jsonify({
                "reply": "Formato de imagem inválido."
            }), 400

        resposta = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": VISION_MODEL,

                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": pergunta
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": imagem
                                }
                            }
                        ]
                    }
                ],

                "temperature": 0.2
            },

            timeout=120
        )

        resultado = resposta.json()

        print("RESPOSTA VISÃO:")
        print(resultado)

        if "choices" not in resultado:

            return jsonify({
                "reply": "Não consegui analisar a imagem.",
                "detalhes": resultado
            }), 500

        texto = resultado["choices"][0]["message"]["content"]

        return jsonify({
            "reply": texto
        })

    except Exception as erro:

        print("ERRO VISÃO:", erro)

        return jsonify({
            "reply": "Ocorreu um erro ao analisar a imagem."
        }), 500


# ===============================
# GERAR IMAGEM
# ===============================

@app.route("/generate-image", methods=["POST"])
def generate_image():

    if not API_KEY:
        return jsonify({
            "reply": "A chave da API não está configurada."
        }), 500

    try:

        dados = request.get_json(silent=True) or {}

        prompt = dados.get("prompt", "").strip()

        if not prompt:
            return jsonify({
                "reply": "Descreve a imagem que queres criar."
            }), 400

        resposta = requests.post(
            "https://openrouter.ai/api/v1/images",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": IMAGE_MODEL,
                "prompt": prompt,
                "n": 1
            },

            timeout=180
        )

        resultado = resposta.json()

        print("RESPOSTA GERAÇÃO:")
        print(resultado)

        if "data" not in resultado or not resultado["data"]:

            return jsonify({
                "reply": "Não foi possível gerar a imagem.",
                "detalhes": resultado
            }), 500

        imagem = resultado["data"][0].get("b64_json")

        if not imagem:

            return jsonify({
                "reply": "A API não devolveu a imagem."
            }), 500

        return jsonify({
            "reply": "Imagem criada com sucesso.",
            "image": "data:image/png;base64," + imagem
        })

    except Exception as erro:

        print("ERRO GERAÇÃO:", erro)

        return jsonify({
            "reply": "Ocorreu um erro ao gerar a imagem."
        }), 500


# ===============================
# INICIAR
# ===============================

if __name__ == "__main__":

    print("🚀 Mello IA online")

    app.run(
        host="0.0.0.0",
        port=5000
    )
