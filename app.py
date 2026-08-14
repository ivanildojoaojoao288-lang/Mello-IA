import os
import logging

import requests

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, auth


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "mello-ia-chave-local-temporaria"
)


# ============================================================
# FIREBASE ADMIN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

FIREBASE_KEY = os.path.join(
    BASE_DIR,
    "firebase-service-account.json"
)

if not os.path.exists(FIREBASE_KEY):

    raise FileNotFoundError(
        "O ficheiro firebase-service-account.json "
        "não foi encontrado."
    )


if not firebase_admin._apps:

    cred = credentials.Certificate(
        FIREBASE_KEY
    )

    firebase_admin.initialize_app(
        cred
    )

    logger.info(
        "Firebase inicializado."
    )


# ============================================================
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

# Pode ser alterado pelo .env.
# openrouter/free escolhe automaticamente
# um modelo gratuito disponível.
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


if OPENROUTER_API_KEY:

    logger.info(
        "OpenRouter configurado."
    )

else:

    logger.warning(
        "OPENROUTER_API_KEY não encontrada."
    )


# ============================================================
# UTILIZADOR ATUAL
# ============================================================

def usuario_atual():

    uid = session.get(
        "firebase_uid"
    )

    if not uid:

        return None

    try:

        usuario = auth.get_user(
            uid
        )

        return usuario

    except Exception as erro:

        logger.error(
            "Erro ao obter utilizador: %s",
            erro
        )

        session.clear()

        return None


def exigir_login():

    return usuario_atual() is not None


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def index():

    if not exigir_login():

        return redirect(
            url_for("login")
        )

    return render_template(
        "chat.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login")
def login():

    if usuario_atual():

        return redirect(
            url_for("index")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTO
# ============================================================

@app.route("/register")
def register():

    if usuario_atual():

        return redirect(
            url_for("index")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN FIREBASE
# ============================================================

@app.route(
    "/auth/firebase",
    methods=["POST"]
)
def firebase_login():

    try:

        dados = request.get_json(
            silent=True
        )

        if not dados:

            return jsonify({

                "success": False,

                "error":
                    "Dados de autenticação ausentes."

            }), 400


        id_token = dados.get(
            "idToken"
        )


        if not id_token:

            return jsonify({

                "success": False,

                "error":
                    "ID token ausente."

            }), 400


        decoded_token = auth.verify_id_token(
            id_token
        )


        uid = decoded_token.get(
            "uid"
        )

        email = decoded_token.get(
            "email",
            ""
        )

        name = decoded_token.get(
            "name",
            ""
        )


        if not uid:

            return jsonify({

                "success": False,

                "error":
                    "Token inválido."

            }), 401


        session["firebase_uid"] = uid

        session["email"] = email

        session["name"] = name


        logger.info(
            "Login efetuado: %s",
            email
        )


        return jsonify({

            "success": True,

            "message":
                "Autenticação efetuada com sucesso.",

            "user": {

                "uid": uid,

                "email": email,

                "name": name

            }

        })


    except Exception as erro:

        logger.exception(
            "Erro na autenticação Firebase."
        )

        return jsonify({

            "success": False,

            "error":
                "Não foi possível validar a autenticação."

        }), 401


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# CHAT
# ============================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    # --------------------------------------------------------
    # AUTENTICAÇÃO
    # --------------------------------------------------------

    if not exigir_login():

        return jsonify({

            "success": False,

            "error":
                "Não autenticado."

        }), 401


    # --------------------------------------------------------
    # DADOS
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


    mensagem = str(
        dados.get(
            "message",
            ""
        )
    ).strip()


    historico_recebido = dados.get(
        "history",
        []
    )


    # --------------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------------

    if not mensagem:

        return jsonify({

            "success": False,

            "error":
                "Mensagem vazia."

        }), 400


    if not OPENROUTER_API_KEY:

        return jsonify({

            "success": False,

            "error":
                "OPENROUTER_API_KEY não configurada."

        }), 500


    # --------------------------------------------------------
    # HISTÓRICO
    # --------------------------------------------------------

    mensagens = [

        {
            "role": "system",

            "content": (
                "Tu és a Mello IA, uma assistente "
                "inteligente desenvolvida pelo "
                "Eng. Ivanildo João Paulo Augusto. "

                "Responde sempre em português. "

                "Sê natural, clara, objetiva e útil. "

                "Para perguntas simples, responde "
                "diretamente. "

                "Para estudos, explica passo a passo. "

                "Para programação, fornece código "
                "correto e uma explicação curta. "

                "Não inventes informações. "

                "Quando não souberes algo, diz claramente "
                "que não tens informação suficiente."
            )
        }

    ]


    # --------------------------------------------------------
    # ADICIONAR HISTÓRICO DO FRONTEND
    # --------------------------------------------------------

    if isinstance(
        historico_recebido,
        list
    ):

        for item in historico_recebido[-10:]:

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
                "assistant"
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

                "role": role,

                "content": content

            })


    # --------------------------------------------------------
    # GARANTIR A PERGUNTA ATUAL
    # --------------------------------------------------------

    mensagens.append({

        "role": "user",

        "content": mensagem

    })


    # --------------------------------------------------------
    # CABEÇALHOS OPENROUTER
    # --------------------------------------------------------

    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "http://localhost:5000",

        "X-Title":
            "Mello IA"

    }


    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload = {

        "model":
            OPENROUTER_MODEL,

        "messages":
            mensagens,

        "max_tokens":
            300,

        "temperature":
            0.5,

        "stream":
            False

    }


    logger.info(
        "Enviando pergunta para OpenRouter. "
        "Modelo=%s | max_tokens=%s",
        OPENROUTER_MODEL,
        300
    )


    # --------------------------------------------------------
    # CHAMADA OPENROUTER
    # --------------------------------------------------------

    try:

        resposta_http = requests.post(

            OPENROUTER_URL,

            headers=headers,

            json=payload,

            timeout=90

        )

    except requests.exceptions.Timeout:

        logger.error(
            "Timeout ao contactar OpenRouter."
        )

        return jsonify({

            "success": False,

            "error":
                "A OpenRouter demorou demasiado para responder."

        }), 504


    except requests.exceptions.RequestException as erro:

        logger.exception(
            "Erro de conexão com OpenRouter: %s",
            erro
        )

        return jsonify({

            "success": False,

            "error":
                "Não foi possível conectar à OpenRouter."

        }), 502


    # --------------------------------------------------------
    # LOG DO STATUS
    # --------------------------------------------------------

    logger.info(
        "OpenRouter respondeu HTTP %s",
        resposta_http.status_code
    )


    # --------------------------------------------------------
    # CONVERTER RESPOSTA
    # --------------------------------------------------------

    try:

        resultado = resposta_http.json()

    except ValueError:

        logger.error(
            "OpenRouter devolveu resposta não-JSON: %s",
            resposta_http.text[:1000]
        )

        return jsonify({

            "success": False,

            "error":
                "A OpenRouter devolveu uma resposta inválida."

        }), 502


    # --------------------------------------------------------
    # ERRO HTTP
    # --------------------------------------------------------

    if not resposta_http.ok:

        logger.error(
            "Erro OpenRouter: %s",
            resultado
        )


        erro_openrouter = (
            resultado
            .get("error", {})
        )


        if isinstance(
            erro_openrouter,
            dict
        ):

            mensagem_erro = (
                erro_openrouter.get(
                    "message"
                )
                or
                erro_openrouter.get(
                    "code"
                )
                or
                "Erro desconhecido da OpenRouter."
            )

        else:

            mensagem_erro = str(
                erro_openrouter
            )


        erro_lower = str(
            mensagem_erro
        ).lower()


        # ----------------------------------------------------
        # CRÉDITOS
        # ----------------------------------------------------

        if (
            resposta_http.status_code == 402
            or
            "credit" in erro_lower
            or
            "credits" in erro_lower
            or
            "afford" in erro_lower
        ):

            return jsonify({

                "success": False,

                "error": (
                    "A chave OpenRouter não tem "
                    "créditos suficientes para esta "
                    "requisição. "
                    "Se estiveres a usar openrouter/free, "
                    "pode ser necessário aguardar o limite "
                    "do modelo gratuito ou verificar os "
                    "limites da conta."
                )

            }), 402


        # ----------------------------------------------------
        # MODELO INDISPONÍVEL
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

                "success": False,

                "error": (
                    "O modelo configurado não está "
                    "disponível neste momento."
                )

            }), 503


        # ----------------------------------------------------
        # OUTRO ERRO
        # ----------------------------------------------------

        return jsonify({

            "success": False,

            "error":
                f"OpenRouter: {mensagem_erro}"

        }), resposta_http.status_code


    # --------------------------------------------------------
    # OBTER CHOICES
    # --------------------------------------------------------

    choices = resultado.get(
        "choices",
        []
    )


    if not choices:

        logger.error(
            "Resposta sem choices: %s",
            resultado
        )

        return jsonify({

            "success": False,

            "error":
                "A Mello IA não recebeu uma resposta do modelo."

        }), 500


    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    mensagem_modelo = (
        choices[0]
        .get(
            "message",
            {}
        )
    )


    texto = mensagem_modelo.get(
        "content",
        ""
    )


    if isinstance(
        texto,
        list
    ):

        partes = []

        for parte in texto:

            if isinstance(
                parte,
                dict
            ):

                if parte.get("type") == "text":

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


    texto = str(
        texto
        or ""
    ).strip()


    if not texto:

        texto = (
            "A Mello IA recebeu a tua pergunta, "
            "mas o modelo não devolveu texto."
        )


    logger.info(
        "Resposta gerada com sucesso."
    )


    # --------------------------------------------------------
    # RESPOSTA AO FRONTEND
    # --------------------------------------------------------

    return jsonify({

        "success":
            True,

        "reply":
            texto,

        "response":
            texto

    })


# ============================================================
# API DO UTILIZADOR
# ============================================================

@app.route(
    "/api/me"
)
def api_me():

    usuario = usuario_atual()


    if not usuario:

        return jsonify({

            "authenticated":
                False

        }), 401


    return jsonify({

        "authenticated":
            True,

        "user": {

            "uid":
                usuario.uid,

            "email":
                usuario.email or "",

            "name": (
                usuario.display_name
                or
                session.get(
                    "name",
                    ""
                )
            )

        }

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health"
)
def health():

    return jsonify({

        "status":
            "online",

        "firebase":
            bool(
                firebase_admin._apps
            ),

        "openrouter":
            bool(
                OPENROUTER_API_KEY
            ),

        "model":
            OPENROUTER_MODEL,

        "max_tokens":
            300

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
        "Firebase: %s",
        "OK"
        if firebase_admin._apps
        else "ERRO"
    )

    logger.info(
        "OpenRouter: %s",
        "OK"
        if OPENROUTER_API_KEY
        else "NÃO CONFIGURADO"
    )

    logger.info(
        "Modelo: %s",
        OPENROUTER_MODEL
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
                5000
            )
        ),

        debug=True

    )
