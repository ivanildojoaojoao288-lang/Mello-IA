import os
import base64
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv


# =====================================================
# MELLO IA — CONFIGURAÇÃO
# =====================================================

load_dotenv()

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

IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-5-image"
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# =====================================================
# PERSONALIDADE DA MELLO IA
# =====================================================

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna,
profissional e amigável.

Foste desenvolvida pelo Eng. Ivanildo João Paulo Augusto.

REGRAS:

- Responde sempre em português.
- Usa linguagem clara e profissional.
- Explica assuntos difíceis de forma simples.
- Ajuda em programação, informática, redes, matemática,
  estudos, tecnologia e informação geral.
- Quando receberes uma imagem, analisa cuidadosamente
  tudo o que estiver visível.
- Podes ler textos presentes em imagens.
- Podes analisar exercícios.
- Podes resolver contas matemáticas.
- Podes analisar códigos fotografados.
- Podes interpretar tabelas e diagramas.
- Se a imagem estiver ilegível, informa claramente.
- Nunca inventes aquilo que não consegues identificar.
- Em matemática, apresenta os passos da resolução.
- Usa Markdown para organizar respostas.
- Usa títulos, listas, tabelas e blocos de código quando
  forem úteis.
- Para código, usa blocos Markdown com a linguagem.
- Não reveles chaves API ou configurações secretas.

Quando perguntarem quem criou a Mello IA, responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João
Paulo Augusto, com foco em inteligência artificial,
programação e inovação tecnológica."
"""


# =====================================================
# PÁGINA
# =====================================================

@app.route("/")
def inicio():
    return render_template("chat.html")


# =====================================================
# IMAGEM → BASE64
# =====================================================

def imagem_para_data_url(arquivo):

    dados = arquivo.read()

    if not dados:
        raise ValueError("A imagem está vazia.")

    mime_type = arquivo.mimetype or "image/jpeg"

    base64_imagem = base64.b64encode(
        dados
    ).decode("utf-8")

    return f"data:{mime_type};base64,{base64_imagem}"


# =====================================================
# OPENROUTER
# =====================================================

def chamar_openrouter(mensagem, imagem=None):

    if not API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY não está configurada."
        )


    # =================================================
    # TEXTO NORMAL
    # =================================================

    if imagem is None:

        payload = {

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
        }


    # =================================================
    # IMAGEM
    # =================================================

    else:

        imagem_url = imagem_para_data_url(
            imagem
        )


        texto = mensagem

        if not texto:

            texto = """
Analisa cuidadosamente esta imagem.

Explica o que está presente.

Se houver:
- texto, lê o texto;
- uma conta, resolve;
- um exercício, explica passo a passo;
- código, explica o código;
- uma tabela, interpreta;
- um documento, resume;
- uma questão, responde.

Não inventes informações que não estejam visíveis.
"""


        conteudo = [

            {
                "type": "text",
                "text": texto
            },

            {
                "type": "image_url",

                "image_url": {
                    "url": imagem_url
                }

            }

        ]


        payload = {

            "model": VISION_MODEL,

            "messages": [

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": conteudo
                }

            ],

            "temperature": 0.4
        }


    # =================================================
    # REQUEST
    # =================================================

    headers = {

        "Authorization":
            f"Bearer {API_KEY}",

        "Content-Type":
            "application/json"

    }


    resposta = requests.post(

        OPENROUTER_URL,

        headers=headers,

        json=payload,

        timeout=120

    )


    print(
        "OPENROUTER STATUS:",
        resposta.status_code
    )


    try:

        resultado = resposta.json()

    except Exception:

        raise ValueError(
            "Resposta inválida do OpenRouter."
        )


    print(
        "OPENROUTER RESPONSE:",
        resultado
    )


    # =================================================
    # ERRO
    # =================================================

    if resposta.status_code != 200:

        erro = resultado.get(
            "error",
            {}
        )

        if isinstance(erro, dict):

            mensagem_erro = erro.get(
                "message",
                "Erro desconhecido."
            )

        else:

            mensagem_erro = str(erro)


        raise ValueError(
            mensagem_erro
        )


    choices = resultado.get(
        "choices"
    )


    if not choices:

        raise ValueError(
            "A IA não devolveu nenhuma resposta."
        )


    message = choices[0].get(
        "message",
        {}
    )


    texto = message.get(
        "content"
    )


    if not texto:

        raise ValueError(
            "A IA devolveu uma resposta vazia."
        )


    return texto


# =====================================================
# CHAT
# =====================================================

@app
