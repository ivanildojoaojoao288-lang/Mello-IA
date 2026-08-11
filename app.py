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
        "A chave firebase-service-account.json não foi encontrada."
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
            "Erro ao obter utilizador: %s",
            erro
        )

        session.clear()

        return None


# ============================================================
# PROTEÇÃO
# ============================================================

def pagina_protegida():

    usuario = usuario_atual()

    if not usuario:

        return redirect(
            url_for("login")
        )

    return None


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def index():

    protecao = pagina_protegida()

    if protecao:
        return protecao

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
# REGISTRO
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
                "error": "Dados de autenticação ausentes."
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

    # Verificar login
    if not usuario_atual():

        return jsonify({

            "success": False,

            "error": "Não autenticado."

        }), 401


    # Ler JSON
    dados = request.get_json(
        silent=True
    )


    if not dados:

        return jsonify({

            "success": False,

            "error": "Dados inválidos."

        }), 400


    mensagem = dados.get(
        "message",
        ""
    )


    if not isinstance(
        mensagem,
        str
    ):

        return jsonify({

            "success": False,

            "error": "Mensagem inválida."

        }), 400


    mensagem = mensagem.strip()


    if not mensagem:

        return jsonify({

            "success": False,

            "error": "Mensagem vazia."

        }), 400


    # Verificar OpenRouter
    if not client:

        return jsonify({

            "success": False,

            "error":
                "OPENROUTER_API_KEY não está configurada."

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
Tu és a Mello IA, uma assistente inteligente
desenvolvida pelo Eng. Ivanildo João Paulo Augusto.

Responde em português de forma natural,
clara, profissional e útil.

Não inventes informações.

Se não souberes alguma coisa,
diz claramente que não tens informação suficiente.

Quando o utilizador estiver a estudar,
explica passo a passo.

Quando for programação,
fornece código correto e explica como utilizar.

Quando houver cálculos,
mostra o raciocínio de forma clara.

Não afirmes que tens acesso a informações
em tempo real se não tiveres.

Não dig
