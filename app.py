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


# =====================================================
# CONFIGURAÇÕES DA IA
# =====================================================

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

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


# =====================================================
# LIMITES
# =====================================================

MAX_IMAGE_SIZE = 10 * 1024 * 1024

MAX_TOKENS_TEXT = 2000
MAX_TOKENS_VISION = 2500

# Número máximo de resultados que a pesquisa Web
# poderá utilizar.
WEB_SEARCH_MAX_RESULTS = 5


# =====================================================
# PERSONALIDADE DA MELLO IA
# =====================================================

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna.

Responde em português de forma clara, profissional,
organizada e útil.

Podes ajudar em:

- programação
- informática
- redes de computadores
- inteligência artificial
- matemática
- estudos
- tecnologia
- explicação de conceitos
- análise de imagens
- leitura de textos em imagens
- resolução de exercícios presentes em imagens
- análise de código presente em imagens
- pesquisa de informações atuais na Web

REGRAS GERAIS:

1. Não inventes informações.

2. Se não souberes ou não conseguires confirmar algo,
   diz claramente que não consegues confirmar.

3. Quando houver matemática, mostra os passos.

4. Quando houver código, explica os erros e apresenta
   uma possível correção.

5. Responde de forma organizada.

6. Não reveles chaves, credenciais ou configurações
   internas do sistema.

PESQUISA E REFERÊNCIAS:

7. Quando a pergunta pedir informações atuais,
   notícias, preços, estatísticas, rankings, vendas,
   acontecimentos recentes ou informações que possam
   ter mudado, pesquisa na Web antes de responder.

8. Quando pesquisares na Web, baseia as afirmações
   importantes nas fontes encontradas.

9. Nunca inventes uma fonte, autor, título, data,
   URL, número de vendas ou referência bibliográfica.

10. No final de uma resposta baseada em pesquisa,
    apresenta uma secção chamada:

    ### Referências

    Lista as principais fontes utilizadas.

11. Para cada referência, apresenta, quando disponível:

    - nome da organização ou autor
    - título da página ou artigo
    - data
    - URL

12. Dá preferência a fontes primárias e confiáveis,
    como:

    - sites oficiais
    - universidades
    - órgãos públicos
    - documentação oficial
    - artigos científicos
    - organizações reconhecidas

13. Se duas fontes apresentarem números diferentes,
    explica a diferença em vez de escolher um número
    arbitrariamente.

14. Não apresentes uma referência como prova de uma
    informação se a fonte não sustentar essa informação.

15. Quando não houver fontes suficientes para confirmar
    uma informação, diz isso claramente.

16. Para trabalhos acadêmicos, quando solicitado,
    organiza as referências de acordo com o estilo
    pedido pelo utilizador, como APA 7ª edição.

IDENTIDADE:

Quando perguntarem quem criou a Mello IA, responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João
Paulo Augusto, com foco em inteligência artificial,
programação e inovação tecnológica."
"""


# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def erro_openrouter(resultado):
    """
    Extrai uma mensagem de erro compreensível
    devolvida pelo OpenRouter.
    """

    if not isinstance(resultado, dict):
        return None

    erro = resultado.get("error")

    if isinstance(erro, dict):
        return erro.get("message")

    return None


def extrair_resposta(resultado):
    """
    Extrai o texto da resposta da IA.
    """

    if not isinstance(resultado, dict):
        return None

    choices = resultado.get("choices")

    if not choices:
        return None

    primeira = choices[0]

    message = primeira.get("message", {})

    if isinstance(message, dict):

        content = message.get("content")

        if isinstance(content, str):
            return content.strip()

    return None


def headers_openrouter():

    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Mello IA"
    }


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

@app.route("/")
def inicio():

    return render_template("chat.html")


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "online",
        "app": "Mello IA",
        "model": MODEL,
        "vision_model": VISION_MODEL,
        "image_model": IMAGE_MODEL,
        "api_key_configurada": bool(API_KEY),
        "web_search": True
    })


# =====================================================
# CHAT
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    # -------------------------------------------------
    # VERIFICAR API KEY
    # -------------------------------------------------

    if not API_KEY:

        logger.error(
            "OPENROUTER_API_KEY não configurada."
        )

        return jsonify({
            "reply":
                "A chave da API não está configurada no servidor."
        }), 500

    try:

        # =================================================
        # RECEBER TEXTO
        # =================================================

        mensagem = ""

        if request.form:

            mensagem = request.form.get(
                "message",
                ""
            ).strip()

        elif request.is_json:

            dados = request.get_json(
                silent=True
            ) or {}

            mensagem = dados.get(
                "message",
                ""
            ).strip()


        # =================================================
        # RECEBER IMAGEM
        # =================================================

        arquivo = request.files.get("image")


        # =================================================
        # VALIDAR PEDIDO
        # =================================================

        if not mensagem and not arquivo:

            return jsonify({
                "reply":
                    "Escreva uma mensagem ou envie uma imagem."
            }), 400


        # =================================================
        # CHAT NORMAL
        # =================================================

        if not arquivo:

            logger.info(
                "Pedido de texto recebido."
            )

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

                # =================================================
                # PESQUISA NA WEB
                # =================================================

                "tools": [

                    {
                        "type": "openrouter:web_search",

                        "parameters": {
                            "max_results":
                                WEB_SEARCH_MAX_RESULTS
                        }
                    }

                ],

                "temperature": 0.7,

                "max_tokens": MAX_TOKENS_TEXT
            }


            logger.info(
                "Enviando pedido de texto para %s",
                MODEL
            )


            resposta = requests.post(

                OPENROUTER_URL,

                headers=headers_openrouter(),

                json=payload,

                timeout=90
            )


            logger.info(
                "OpenRouter texto: HTTP %s",
                resposta.status_code
            )


            try:

                resultado = resposta.json()

            except ValueError:

                logger.error(
                    "Resposta inválida do OpenRouter."
                )

                return jsonify({
                    "reply":
                        "O servidor da IA devolveu uma resposta inválida."
                }), 502


            # =================================================
            # ERRO OPENROUTER
            # =================================================

            if resposta.status_code >= 400:

                mensagem_erro = erro_openrouter(
                    resultado
                )

                logger.error(
                    "Erro OpenRouter: %s",
                    resultado
                )

                return jsonify({

                    "reply":
                        mensagem_erro
                        or
                        "A IA recusou o pedido."

                }), 502


            # =================================================
            # EXTRAIR RESPOSTA
            # =================================================

            texto = extrair_resposta(
                resultado
            )


            if not texto:

                return jsonify({
                    "reply":
                        "A IA não devolveu nenhuma resposta."
                }), 502


            return jsonify({
                "reply": texto
            })


        # =================================================
        # ANÁLISE DE IMAGEM
        # =================================================

        tipo = arquivo.content_type or ""


        if not tipo.startswith("image/"):

            return jsonify({
                "reply":
                    "O ficheiro enviado não é uma imagem válida."
            }), 400


        # =================================================
        # LIMITE DE TAMANHO
        # =================================================

        arquivo.seek(0, os.SEEK_END)

        tamanho = arquivo.tell()

        arquivo.seek(0)


        if tamanho > MAX_IMAGE_SIZE:

            return jsonify({
                "reply":
                    "A imagem deve ter no máximo 10 MB."
            }), 400


        # =================================================
        # CONVERTER PARA BASE64
        # =================================================

        dados_imagem = arquivo.read()

        imagem_base64 = base64.b64encode(
            dados_imagem
        ).decode("utf-8")


        data_url = (
            f"data:{tipo};base64,{imagem_base64}"
        )


        # =================================================
        # PERGUNTA PADRÃO
        # =================================================

        if not mensagem:

            mensagem = """
Analisa cuidadosamente esta imagem.

Explica de forma organizada tudo o que
conseguires identificar.

Se houver texto, lê e explica.

Se houver uma questão matemática,
resolve passo a passo.

Se houver código, identifica possíveis
erros e explica como corrigir.

Não inventes informações que não estejam
visíveis na imagem.
"""


        # =================================================
        # PEDIDO PARA MODELO DE VISÃO
        # =================================================

        payload = {

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
                            "text": mensagem
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

            "temperature": 0.4,

            "max_tokens": MAX_TOKENS_VISION
        }


        logger.info(
            "Enviando imagem para %s",
            VISION_MODEL
        )


        resposta = requests.post(

            OPENROUTER_URL,

            headers=headers_openrouter(),

            json=payload,

            timeout=120
        )


        logger.info(
            "OpenRouter visão: HTTP %s",
            resposta.status_code
        )


        try:

            resultado = resposta.json()

        except ValueError:

            return jsonify({
                "reply":
                    "O servidor da IA devolveu uma resposta inválida."
            }), 502


        # =================================================
        # ERRO DA VISÃO
        # =================================================

        if resposta.status_code >= 400:

            mensagem_erro = erro_openrouter(
                resultado
            )

            logger.error(
                "Erro visão OpenRouter: %s",
                resultado
            )

            return jsonify({

                "reply":
                    mensagem_erro
                    or
                    "Não foi possível analisar a imagem."

            }), 502


        # =================================================
        # EXTRAIR RESPOSTA
        # =================================================

        texto = extrair_resposta(
            resultado
        )


        if not texto:

            return jsonify({
                "reply":
                    "A IA não conseguiu analisar esta imagem."
            }), 502


        return jsonify({
            "reply": texto
        })


    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        logger.exception(
            "Timeout na comunicação com OpenRouter."
        )

        return jsonify({

            "reply":
                "A IA demorou demasiado para responder. "
                "Tenta novamente."

        }), 504


    # =====================================================
    # ERRO DE REDE
    # =====================================================

    except requests.exceptions.RequestException as erro:

        logger.exception(
            "Erro de comunicação: %s",
            erro
        )

        return jsonify({

            "reply":
                "Erro de comunicação com o servidor da IA."

        }), 502


    # =====================================================
    # ERRO GERAL
    # =====================================================

    except Exception as erro:

        logger.exception(
            "Erro interno: %s",
            erro
        )

        return jsonify({

            "reply":
                "Erro interno da Mello IA."

        }), 500


# =====================================================
# EXECUTAR
# =====================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("       MELLO IA — SERVIDOR ONLINE")
    print("==========================================")
    print("Modelo:", MODEL)
    print("Vision:", VISION_MODEL)
    print("Imagem:", IMAGE_MODEL)
    print("API configurada:", bool(API_KEY))
    print("Pesquisa Web: ATIVADA")
    print("URL: http://127.0.0.1:5000")
    print("==========================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
