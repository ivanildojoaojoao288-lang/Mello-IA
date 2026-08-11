import os
import logging

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
# AUTENTICAÇÃO
# ============================================================

def usuario_atual():

    uid = session.get("firebase_uid")

    if not uid:
        return None

    try:

        usuario = auth.get_user(uid)

        return usuario

    except Exception as erro:

        logger.error(
            "Erro ao obter utilizador: %s",
            erro
        )

        session.clear()

        return None


def pagina_protegida():

    usuario = usuario_atual()

    if not usuario:

        return redirect(
            url_for("login")
        )

    return None


# ============================================================
# PÁGINAS
# ============================================================

@app.route("/")
def index():

    protecao = pagina_protegida()

    if protecao:
        return protecao

    return render_template(
        "chat.html"
    )


@app.route("/login")
def login():

    if usuario_atual():

        return redirect(
            url_for("index")
        )

    return render_template(
        "login.html"
    )


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
# FIREBASE TOKEN
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
                "error": "Dados de autenticação ausentes."
            }), 400

        id_token = dados.get(
            "idToken"
        )

        if not id_token:

            return jsonify({
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
            "message": "Autenticação efetuada com sucesso.",
            "user": {
                "uid": uid,
                "email": email,
                "name": name
            }
        })

    except Exception:

        logger.exception(
            "Erro na autenticação Firebase."
        )

        return jsonify({
            "error": "Não foi possível validar a autenticação."
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

    protecao = pagina_protegida()

    if protecao:

        return jsonify({
            "error": "Não autenticado."
        }), 401


    # ========================================================
    # ACEITAR JSON OU FORMDATA
    # ========================================================

    if request.is_json:

        dados = request.get_json(
            silent=True
        ) or {}

        mensagem = dados.get(
            "message",
            ""
        ).strip()

    else:

        mensagem = request.form.get(
            "message",
            ""
        ).strip()


    # ========================================================
    # VALIDAR MENSAGEM
    # ========================================================

    if not mensagem:

        return jsonify({
            "error": "Mensagem vazia."
        }), 400


    # ========================================================
    # VERIFICAR OPENROUTER
    # ========================================================

    if not client:

        return jsonify({
            "error": "A API da Mello IA ainda não está configurada no servidor."
        }), 500


    # ========================================================
    # PROCESSAR IA
    # ========================================================

    try:

        resposta = client.chat.completions.create(

            model="meta-llama/llama-3.1-8b-instruct",

            # Limite reduzido para funcionar
            # com o crédito disponível.
            max_tokens=500,

            messages=[

                {
                    "role": "system",
                    "content": """
Tu és a Mello IA, uma assistente inteligente desenvolvida por
Eng. Ivanildo João Paulo Augusto.

Responde em português de forma natural, humana, clara e útil.

Não fales como um robô.

Não digas que pesquisaste na Internet quando não fizeste uma pesquisa.

Não afirmes que tens acesso a informações em tempo real se não tiveres.

Explica assuntos difíceis de maneira simples quando o utilizador pedir.

Quando o utilizador estiver a estudar, ensina passo a passo.

Quando for programação, fornece código correto e explica como utilizar.

Sê profissional, mas conversa de forma natural.

Mantém as respostas objetivas para evitar consumo desnecessário de tokens.
"""
                },

                {
                    "role": "user",
                    "content": mensagem
                }

            ]

        )


        # ====================================================
        # OBTER RESPOSTA
        # ====================================================

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


        logger.info(
            "Resposta da Mello IA gerada com sucesso."
        )


        # ====================================================
        # RETORNO
        # ====================================================

        return jsonify({

            "success": True,

            # Campo usado pelo frontend
            "reply": texto,

            # Mantemos também response
            # para compatibilidade.
            "response": texto

        })


    except Exception as erro:

        logger.exception(
            "Erro no processamento da Mello IA."
        )


        return jsonify({

            "success": False,

            "error": (
                "Ocorreu um erro ao processar a mensagem."
            ),

            "reply": (
                "Não consegui processar a tua mensagem neste momento."
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

            "email": usuario.email,

            "name": usuario.display_name or ""

        }

    })


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    logger.info(
        "Mello IA iniciando..."
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
