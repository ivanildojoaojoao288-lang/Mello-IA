import os
import logging
import requests

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
)

from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = Flask(__name__)


# ============================================================
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "",
).strip()

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free",
).strip()

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


# ============================================================
# LIMITE FIXO
# ============================================================

# FIXO EM 300.
# Não depende do .env.
# Não pode virar 2000, 16384, 65536 etc.
MAX_TOKENS = 300

TEMPERATURE = 0.5


# ============================================================
# LOG INICIAL
# ============================================================

logger.info(
    "======================================"
)

logger.info(
    "MELLO IA INICIANDO..."
)

logger.info(
    "OpenRouter: %s",
    "OK"
    if OPENROUTER_API_KEY
    else "NÃO CONFIGURADO",
)

logger.info(
    "Modelo: %s",
    OPENROUTER_MODEL,
)

logger.info(
    "Max tokens: %s",
    MAX_TOKENS,
)

logger.info(
    "======================================"
)


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def index():

    # SEM FIREBASE
    # SEM LOGIN OBRIGATÓRIO

    return render_template(
        "chat.html"
    )


# ============================================================
# CHAT
# ============================================================

@app.route(
    "/chat",
    methods=["POST"],
)
def chat():

    # --------------------------------------------------------
    # VERIFICAR OPENROUTER
    # --------------------------------------------------------

    if not OPENROUTER_API_KEY:

        logger.error(
            "OPENROUTER_API_KEY não configurada."
        )

        return jsonify({

            "success": False,

            "error":
                "A chave da OpenRouter não está configurada."

        }), 500


    # --------------------------------------------------------
    # RECEBER JSON
    # --------------------------------------------------------

    dados = request.get_json(
        silent=True
    )


    if not dados:

        return jsonify({

            "success": False,

            "error":
                "Dados inválidos."

        }), 400


    # --------------------------------------------------------
    # MENSAGEM
    # --------------------------------------------------------

    mensagem = str(
        dados.get(
            "message",
            "",
        )
    ).strip()


    # --------------------------------------------------------
    # HISTÓRICO
    # --------------------------------------------------------

    historico = dados.get(
        "history",
        []
    )


    # --------------------------------------------------------
    # VALIDAR MENSAGEM
    # --------------------------------------------------------

    if not mensagem:

        return jsonify({

            "success": False,

            "error":
                "Escreve uma mensagem primeiro."

        }), 400


    # ========================================================
    # MENSAGENS
    # ========================================================

    mensagens = [

        {
            "role": "system",

            "content": (
                "Tu és a Mello IA, uma assistente "
                "inteligente desenvolvida pelo "
                "Eng. Ivanildo João Paulo Augusto. "

                "Responde em português. "

                "Sê natural, clara, objetiva e útil. "

                "Para perguntas simples, responde "
                "diretamente. "

                "Para perguntas escolares, explica "
                "passo a passo. "

                "Para matemática, apresenta os cálculos "
                "necessários. "

                "Para programação, fornece código correto "
                "e explica como usar. "

                "Não inventes informações. "

                "Se não souberes algo, diz claramente."
            ),
        }

    ]


    # ========================================================
    # HISTÓRICO
    # ========================================================

    if isinstance(
        historico,
        list
    ):

        for item in historico[-6:]:

            if not isinstance(
                item,
                dict
            ):
                continue


            role = item.get(
                "role"
            )

            content = item.get(
                "content"
            )


            if role not in (
                "user",
                "assistant",
            ):
                continue


            if not isinstance(
                content,
                str
            ):
                continue


            content = content.strip()


            if not content:
                continue


            mensagens.append({

                "role":
                    role,

                "content":
                    content[:1500],

            })


    # ========================================================
    # MENSAGEM ATUAL
    # ========================================================

    mensagens.append({

        "role":
            "user",

        "content":
            mensagem[:3000],

    })


    # ========================================================
    # HEADERS
    # ========================================================

    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            os.getenv(
                "APP_URL",
                "http://localhost:5000",
            ),

        "X-Title":
            "Mello IA",

    }


    # ========================================================
    # PAYLOAD
    # ========================================================

    payload = {

        "model":
            OPENROUTER_MODEL,

        "messages":
            mensagens,

        # ====================================================
        # IMPORTANTE
        # ====================================================
        # NÃO ALTERAR PARA 2000.
        # NÃO VEM DO .ENV.
        # FICA FIXO EM 300.
        #
        "max_tokens":
            300,

        "temperature":
            TEMPERATURE,

        "stream":
            False,

    }


    # ========================================================
    # LOG
    # ========================================================

    logger.info(
        "Pedido de texto recebido."
    )

    logger.info(
        "Modelo enviado: %s",
        payload["model"],
    )

    logger.info(
        "Max tokens enviado: %s",
        payload["max_tokens"],
    )


    # ========================================================
    # REQUISIÇÃO
    # ========================================================

    try:

        resposta = requests.post(

            OPENROUTER_URL,

            headers=headers,

            json=payload,

            timeout=90,

        )


    except requests.exceptions.Timeout:

        logger.error(
            "Timeout na OpenRouter."
        )

        return jsonify({

            "success":
                False,

            "error":
                "A OpenRouter demorou demasiado para responder.",

        }), 504


    except requests.exceptions.RequestException as erro:

        logger.exception(
            "Erro de conexão com OpenRouter: %s",
            erro,
        )

        return jsonify({

            "success":
                False,

            "error":
                "Não foi possível conectar à OpenRouter.",

        }), 502


    # ========================================================
    # STATUS
    # ========================================================

    logger.info(
        "OpenRouter respondeu HTTP %s",
        resposta.status_code,
    )


    # ========================================================
    # JSON
    # ========================================================

    try:

        resultado = resposta.json()

    except ValueError:

        logger.error(
            "OpenRouter devolveu resposta que não é JSON."
        )

        return jsonify({

            "success":
                False,

            "error":
                "Resposta inválida da OpenRouter.",

        }), 502


    # ========================================================
    # ERRO
    # ========================================================

    if not resposta.ok:

        logger.error(
            "Erro OpenRouter: %s",
            resultado,
        )


        erro = resultado.get(
            "error",
            {},
        )


        if isinstance(
            erro,
            dict
        ):

            mensagem_erro = (

                erro.get(
                    "message"
                )

                or

                erro.get(
                    "code"
                )

                or

                "Erro desconhecido da OpenRouter."

            )

        else:

            mensagem_erro = str(
                erro
            )


        erro_lower = str(
            mensagem_erro
        ).lower()


        # ----------------------------------------------------
        # 402
        # ----------------------------------------------------

        if (
            resposta.status_code == 402

            or

            "credit" in erro_lower

            or

            "credits" in erro_lower

            or

            "afford" in erro_lower
        ):

            logger.error(
                "OpenRouter sem créditos suficientes."
            )

            return jsonify({

                "success":
                    False,

                "error": (
                    "A OpenRouter recusou a solicitação "
                    "porque a conta/chave não tem créditos "
                    "suficientes para este modelo."
                ),

            }), 402


        # ----------------------------------------------------
        # MODELO
        # ----------------------------------------------------

        if (
            "model" in erro_lower
            and
            (
                "not found" in erro_lower
                or
                "unavailable" in erro_lower
            )
        ):

            return jsonify({

                "success":
                    False,

                "error": (
                    "O modelo configurado não está "
                    "disponível neste momento."
                ),

            }), 503


        # ----------------------------------------------------
        # ERRO GENÉRICO
        # ----------------------------------------------------

        return jsonify({

            "success":
                False,

            "error":
                f"OpenRouter: {mensagem_erro}",

        }), resposta.status_code


    # ========================================================
    # CHOICES
    # ========================================================

    choices = resultado.get(
        "choices",
        []
    )


    if not choices:

        logger.error(
            "OpenRouter não devolveu choices: %s",
            resultado,
        )

        return jsonify({

            "success":
                False,

            "error":
                "A IA não devolveu uma resposta.",

        }), 500


    # ========================================================
    # MESSAGE
    # ========================================================

    message = choices[0].get(
        "message",
        {}
    )


    texto = message.get(
        "content",
        ""
    )


    # ========================================================
    # CONTENT LISTA
    # ========================================================

    if isinstance(
        texto,
        list
    ):

        partes = []


        for parte in texto:

            if not isinstance(
                parte,
                dict
            ):
                continue


            if parte.get(
                "type"
            ) == "text":

                partes.append(
                    str(
                        parte.get(
                            "text",
                            ""
                        )
                    )
                )


        texto = "\n".join(
            partes
        )


    # ========================================================
    # TEXTO FINAL
    # ========================================================

    texto = str(
        texto or ""
    ).strip()


    if not texto:

        texto = (
            "Não consegui gerar uma resposta."
        )


    logger.info(
        "Resposta gerada com sucesso."
    )


    # ========================================================
    # RESPOSTA PARA O FRONTEND
    # ========================================================

    return jsonify({

        "success":
            True,

        "reply":
            texto,

        "response":
            texto,

    })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "online",

        "openrouter":
            bool(
                OPENROUTER_API_KEY
            ),

        "model":
            OPENROUTER_MODEL,

        "max_tokens":
            300,

    })


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    logger.info(
        "======================================"
    )

    logger.info(
        "MELLO IA INICIANDO..."
    )

    logger.info(
        "OpenRouter: %s",
        "OK"
        if OPENROUTER_API_KEY
        else "NÃO CONFIGURADO",
    )

    logger.info(
        "Modelo: %s",
        OPENROUTER_MODEL,
    )

    logger.info(
        "Max tokens: 300"
    )

    logger.info(
        "======================================"
    )


    app.run(

        host="0.0.0.0",

        port=int(
            os.getenv(
                "PORT",
                "5000",
            )
        ),

        debug=True,

    )
