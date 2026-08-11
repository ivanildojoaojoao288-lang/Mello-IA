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
# FIREBASE
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
        "firebase-service-account.json não foi encontrado."
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

        return auth.get_user(
            uid
        )

    except Exception as erro:

        logger.error(
            "Erro Firebase: %s",
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
                "error": "Dados ausentes."
            }), 400

        token = dados.get(
            "idToken"
        )

        if not token:

            return jsonify({
                "success": False,
                "error": "Token Firebase ausente."
            }), 400

        decoded = auth.verify_id_token(
            token
        )

        uid = decoded.get(
            "uid"
        )

        email = decoded.get(
            "email",
            ""
        )

        name = decoded.get(
            "name",
            ""
        )

        if not uid:

            return jsonify({
                "success": False,
                "error": "UID inválido."
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
            "message": "Login efetuado com sucesso.",
            "user": {
                "uid": uid,
                "email": email,
                "name": name
            }
        })

    except Exception as erro:

        logger.exception(
            "Erro no login Firebase: %s",
            erro
        )

        return jsonify({
            "success": False,
            "error": "Falha na autenticação Firebase."
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
            "error": "OPENROUTER_API_KEY não configurada."
        }), 500

    try:

        resposta = client.chat.completions.create(

            model=os.getenv(
                "OPENROUTER_MODEL",
                "meta-llama/llama-3.1-8b-instruct"
            ),

            messages=[

                {
                    "role": "system",

                    "content": """
Tu és a Mello IA.

Foste desenvolvida pelo
Eng. Ivanildo João Paulo Augusto.

Responde em português.

Sê clara, natural, profissional e útil.

Não inventes informações.

Quando explicares uma matéria,
faz isso passo a passo.

Quando ajudares com programação,
fornece código correto e explica
como executar.

Não digas que tens acesso à
Internet ou informações em tempo
real se não tiveres.

Se não souberes alguma informação,
diz claramente que não tens dados
suficientes para confirmar.
                },

                {
                    "role": "user",
                    "content": mensagem
                }

            ],

            max_tokens=2000,

            temperature=0.7
        )

        if not resposta.choices:

            return jsonify({
                "success": False,
                "error": "A IA não devolveu uma resposta."
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
            "Erro OpenRouter."
        )

        mensagem_erro = str(
            erro
        )

        if (
            "credit" in mensagem_erro.lower()
            or "credits" in mensagem_erro.lower()
        ):

            return jsonify({

                "success": False,

                "error": (
                    "A OpenRouter recusou a resposta "
                    "porque a chave não possui créditos "
                    "suficientes para 2000 tokens."
                )

            }), 402

        return jsonify({

            "success": False,

            "error": (
                "Erro ao comunicar com a OpenRouter."
            )

        }), 500


# ============================================================
# UTILIZADOR
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

            "email": usuario.email or "",

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
        )

    })


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    logger.info(
        "===================================="
    )

    logger.info(
        "MELLO IA INICIANDO..."
    )

    logger.info(
        "Firebase: OK"
    )

    logger.info(
        "OpenRouter: %s",
        "OK" if client else "NÃO CONFIGURADO"
    )

    logger.info(
        "===================================="
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
