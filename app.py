import os
import logging

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

from openai import OpenAI


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
        "A chave firebase-service-account.json "
        "não foi encontrada."
    )

if not firebase_admin._apps:

    cred = credentials.Certificate(
        FIREBASE_KEY
    )

    firebase_admin.initialize_app(
        cred
    )

    logger.info(
        "Firebase Admin inicializado."
    )


# ============================================================
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

client = None

if OPENROUTER_API_KEY:

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )

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
                "error": (
                    "Dados de autenticação ausentes."
                )
            }), 400

        id_token = dados.get(
            "idToken"
        )

        if not id_token:

            return jsonify({
                "success": False,
                "error": "ID token ausente."
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
                "error": "Token inválido."
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

            "message": (
                "Autenticação efetuada com sucesso."
            ),

            "user": {
                "uid": uid,
                "email": email,
                "name": name
            }

        })

    except Exception as erro:

        logger.exception(
            "Erro na autenticação Firebase: %s",
            erro
        )

        return jsonify({

            "success": False,

            "error": (
                "Não foi possível validar "
                "a autenticação Firebase."
            )

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

    if not exigir_login():

        return jsonify({

            "success": False,

            "error": "Não autenticado."

        }), 401

    dados = request.get_json(
        silent=True
    )

    if not dados:

        return jsonify({

            "success": False,

            "error": "Dados inválidos."

        }), 400

    mensagem = str(
        dados.get(
            "message",
            ""
        )
    ).strip()

    if not mensagem:

        return jsonify({

            "success": False,

            "error": "Mensagem vazia."

        }), 400

    if not client:

        return jsonify({

            "success": False,

            "error": (
                "OPENROUTER_API_KEY "
                "não está configurada."
            )

        }), 500

    try:

        resposta = client.chat.completions.create(

            model=OPENROUTER_MODEL,

            messages=[

                {
                    "role": "system",

                    "content": (
                        "Tu és a Mello IA, uma assistente "
                        "inteligente desenvolvida pelo "
                        "Eng. Ivanildo João Paulo Augusto. "
                        "Responde em português de forma "
                        "natural, clara, profissional e útil. "
                        "Não inventes informações. "
                        "Quando o utilizador estiver a estudar, "
                        "explica passo a passo. "
                        "Quando for programação, fornece "
                        "código correto e explica como utilizar. "
                        "Não afirmes ter acesso a informações "
                        "em tempo real se não tiveres."
                    )
                },

                {
                    "role": "user",
                    "content": mensagem
                }

            ],

            max_tokens=500,

            temperature=0.7
        )

        if not resposta.choices:

            return jsonify({

                "success": False,

                "error": (
                    "A IA não devolveu uma resposta."
                )

            }), 500

        texto = (
            resposta
            .choices[0]
            .message
            .content
        )

        if not texto:

            texto = (
                "Não consegui gerar uma resposta."
            )

        return jsonify({

            "success": True,

            "response": texto,

            "reply": texto

        })

    except Exception as erro:

        logger.exception(
            "Erro no processamento da Mello IA."
        )

        erro_texto = str(
            erro
        ).lower()

        if (
            "credit" in erro_texto
            or "credits" in erro_texto
            or "402" in erro_texto
        ):

            return jsonify({

                "success": False,

                "error": (
                    "A OpenRouter recusou a solicitação "
                    "porque a chave não possui créditos "
                    "suficientes."
                )

            }), 402

        return jsonify({

            "success": False,

            "error": (
                "Erro ao comunicar com a OpenRouter."
            )

        }), 500


# ============================================================
# INFORMAÇÕES DO UTILIZADOR
# ============================================================

@app.route("/api/me")
def api_me():

    usuario = usuario_atual()

    if not usuario:

        return jsonify({

            "authenticated": False

        }), 401

    return jsonify({

        "authenticated": True,

        "user": {

            "uid": usuario.uid,

            "email": (
                usuario.email or ""
            ),

            "name": (
                usuario.display_name
                or session.get("name", "")
            )

        }

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "online",

        "firebase": bool(
            firebase_admin._apps
        ),

        "openrouter": bool(
            OPENROUTER_API_KEY
        ),

        "model": OPENROUTER_MODEL,

        "max_tokens": 500

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
        if client
        else "NÃO CONFIGURADO"
    )

    logger.info(
        "Modelo: %s",
        OPENROUTER_MODEL
    )

    logger.info(
        "Max tokens: 500"
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
