import os
import base64
import logging

import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# =====================================================
# CONFIGURAÇÃO
# =====================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna.

Responde em português de forma clara, profissional e útil.

És especializada em:
- programação
- informática
- redes de computadores
- inteligência artificial
- matemática
- estudos
- tecnologia
- explicação e análise de imagens

Quando o utilizador enviar uma imagem:
1. Analisa cuidadosamente a imagem.
2. Explica o que aparece nela.
3. Se houver texto, lê e explica o texto.
4. Se houver uma questão matemática, resolve passo a passo.
5. Se houver código, identifica e explica os erros.
6. Se houver um exercício, apresenta a resolução de forma organizada.
7. Não inventes informações que não estejam visíveis.

Quando perguntarem quem criou a Mello IA, responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João Paulo Augusto, com foco em inteligência artificial, programação e inovação tecnológica."
"""


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

@app.route("/")
def inicio():
    return render_template("chat.html")


# =====================================================
# TESTE DO SERVIDOR
# =====================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "app": "Mello IA",
        "model": MODEL,
        "vision_model": VISION_MODEL,
        "api_key": bool(API_KEY)
    })


# =====================================================
# CHAT
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    if not API_KEY:
        logger.error("OPENROUTER_API_KEY não configurada.")

        return jsonify({
            "reply": "A chave da API não está configurada no servidor."
        }), 500

    try:

        # -------------------------------------------------
        # RECEBER DADOS
        # -------------------------------------------------

        mensagem = ""

        arquivo = request.files.get("image")

        if request.form:
            mensagem = request.form.get(
                "message",
                ""
            ).strip()

        # Também permite JSON quando não existe imagem
        if not request.form and request.is_json:
            dados = request.get_json(silent=True) or {}
            mensagem = dados.get(
                "message",
                ""
            ).strip()

        # -------------------------------------------------
        # SEM TEXTO E SEM IMAGEM
        # -------------------------------------------------

        if not mensagem and not arquivo:

            return jsonify({
                "reply": "Escreva uma mensagem ou envie uma imagem."
            }), 400

        # -------------------------------------------------
        # SEM IMAGEM — CHAT NORMAL
        # -------------------------------------------------

        if not arquivo:

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

                timeout=90
            )

            logger.info(
                "OpenRouter texto: %s",
                resposta.status_code
            )

            try:
                resultado = resposta.json()
            except Exception:
                return jsonify({
                    "reply": "O servidor da IA devolveu uma resposta inválida."
                }), 502

            logger.info(
                "Resposta OpenRouter: %s",
                resultado
            )

            if resposta.status_code >= 400:

                erro = (
                    resultado.get("error", {})
                    if isinstance(resultado, dict)
                    else {}
                )

                mensagem_erro = (
                    erro.get("message")
                    if isinstance(erro, dict)
                    else None
                )

                return jsonify({
                    "reply": mensagem_erro
                    or "A IA recusou o pedido. Verifique o modelo e a chave da API."
                }), 502

            choices = resultado.get("choices")

            if not choices:

                return jsonify({
                    "reply": "A IA não devolveu nenhuma resposta."
                }), 502

            texto = choices[0]["message"]["content"]

            return jsonify({
                "reply": texto
            })

        # -------------------------------------------------
        # IMAGEM
        # -------------------------------------------------

        tipo = arquivo.content_type or ""

        if not tipo.startswith("image/"):

            return jsonify({
                "reply": "O ficheiro enviado não é uma imagem válida."
            }), 400

        # Limite de 10 MB
        arquivo.seek(0, 2)
        tamanho = arquivo.tell()
        arquivo.seek(0)

        if tamanho > 10 * 1024 * 1024:

            return jsonify({
                "reply": "A imagem deve ter no máximo 10 MB."
            }), 400

        dados_imagem = arquivo.read()

        imagem_base64 = base64.b64encode(
            dados_imagem
        ).decode("utf-8")

        data_url = (
            f"data:{tipo};base64,{imagem_base64}"
        )

        pergunta = mensagem

        if not pergunta:

            pergunta = (
                "Analisa esta imagem cuidadosamente. "
                "Explica tudo o que conseguires identificar. "
                "Se houver texto, transcreve e explica. "
                "Se houver uma questão ou cálculo, resolve passo a passo."
            )

        # -------------------------------------------------
        # MODELO DE VISÃO
        # -------------------------------------------------

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
                                    "url": data_url
                                }
                            }
                        ]
                    }
                ],

                "temperature": 0.5
            },

            timeout=120
        )

        logger.info(
            "OpenRouter visão: %s",
            resposta.status_code
        )

        try:
            resultado = resposta.json()

        except Exception:

            return jsonify({
                "reply": "O servidor da IA devolveu uma resposta inválida."
            }), 502

        logger.info(
            "Resposta visão: %s",
            resultado
        )

        if resposta.status_code >= 400:

            erro = resultado.get(
                "error",
                {}
            )

            mensagem_erro = (
                erro.get("message")
                if isinstance(erro, dict)
                else None
            )

            return jsonify({
                "reply":
                    mensagem_erro
                    or "Não foi possível analisar a imagem."
            }), 502

        choices = resultado.get("choices")

        if not choices:

            return jsonify({
                "reply": "A IA não conseguiu analisar esta imagem."
            }), 502

        texto = choices[0]["message"]["content"]

        return jsonify({
            "reply": texto
        })

    # =====================================================
    # ERROS
    # =====================================================

    except requests.exceptions.Timeout:

        logger.exception("Timeout na comunicação com OpenRouter.")

        return jsonify({
            "reply": "A IA demorou demasiado para responder. Tenta novamente."
        }), 504

    except requests.exceptions.RequestException as erro:

        logger.exception(
            "Erro de comunicação com OpenRouter: %s",
            erro
        )

        return jsonify({
            "reply": "Erro de comunicação com o servidor da IA."
        }), 502

    except Exception as erro:

        logger.exception(
            "Erro interno: %s",
            erro
        )

        return jsonify({
            "reply": "Erro interno da Mello IA."
        }), 500


# =====================================================
# EXECUTAR
# =====================================================

if __name__ == "__main__":

    print("==========================================")
    print("       MELLO IA — SERVIDOR ONLINE")
    print("==========================================")
    print("Modelo:", MODEL)
    print("Modelo Vision:", VISION_MODEL)
    print("API configurada:", bool(API_KEY))
    print("URL: http://127.0.0.1:5000")
    print("==========================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
