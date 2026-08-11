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
        "não foi encontrada na pasta do projeto."
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
# OPENROUTER / MELLO IA
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


# ============================================================
# PROTEGER PÁGINA
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
# FIREBASE LOGIN
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

        if not dados
