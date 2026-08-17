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
    session,
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
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "mello-ia-chave-local-temporaria-change-me",
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

if os.getenv("RENDER", "").lower() == "true":
    app.config["SESSION_COOKIE_SECURE"] = True


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

# Nunca permitir que uma variável externa aumente o limite
# acima de 300 nesta versão.
try:
    MAX_TOKENS = int(
        os.getenv("MAX_TOKENS", "300")
    )
except (TypeError, ValueError):
    MAX_TOKENS = 300

MAX_TOKENS = max(
    1,
    min(MAX_TOKENS, 300),
)

TEMPERATURE = 0.5


# ============================================================
# FIREBASE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RENDER_FIREBASE_KEY = (
    "/etc/secrets/firebase-service-account.json"
)

LOCAL_FIREBASE_KEY = os.path.join(
    BASE_DIR,
    "firebase-service-account.json"
)

if os.path.isfile(RENDER_FIREBASE_KEY):
    FIREBASE_KEY = RENDER_FIREBASE_KEY
elif os.path.isfile(LOCAL_FIREBASE_KEY):
    FIREBASE_KEY = LOCAL_FIREBASE_KEY
else:
    FIREBASE_KEY = None


def inicializar_firebase():
    if firebase_admin._apps:
        logger.info("Firebase Admin já estava inicializado.")
        return True

    if not FIREBASE_KEY:
        logger.error(
            "Credencial Firebase não encontrada."
        )
        return False

    try:
        cred = credentials.Certificate(
            FIREBASE_KEY
        )

        firebase_admin.initialize_app(
            cred
        )

        logger.info(
            "Firebase Admin inicializado."
        )

        return True

    except Exception as erro:
        logger.exception(
            "Erro ao inicializar Firebase: %s",
            erro,
        )
        return False


FIREBASE_OK = inicializar_firebase()


# ============================================================
# LOG DE CONFIGURAÇÃO
# ============================================================

logger.info(
    "OpenRouter: %s",
    "configurado" if OPENROUTER_API_KEY else "não configurado",
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
    "Firebase: %s",
    "OK" if FIREBASE_OK else "ERRO",
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

    if not firebase_admin._apps:
        return None

    try:
        return auth.get_user(
            uid
        )

    except Exception as erro:
        logger.error(
            "Erro ao obter utilizador Firebase: %s",
            erro,
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
    methods=["POST"],
)
def firebase_login():
    if not FIREBASE_OK:
        return jsonify({
            "success": False,
            "error": (
                "Firebase Admin não está configurado "
                "no servidor."
            ),
        }), 500

    try:
        dados = request.get_json(
            silent=True
        )

        if not dados:
            return jsonify({
                "success": False,
                "error": "Dados de autenticação ausentes.",
            }), 400

        id_token = str(
            dados.get("idToken", "")
        ).strip()

        if not id_token:
            return jsonify({
                "success": False,
                "error": "ID token ausente.",
            }), 400

        decoded_token = auth.verify_id_token(
            id_token
        )

        uid = decoded_token.get(
            "uid"
        )

        email = decoded_token.get(
            "email",
            "",
        )

        name = decoded_token.get(
            "name",
            "",
        )

        if not uid:
            return jsonify({
                "success": False,
                "error": "Token Firebase inválido.",
            }), 401

        session["firebase_uid"] = uid
        session["email"] = email
        session["name"] = name

        logger.info(
            "Login Firebase efetuado: %s",
            email,
        )

        return jsonify({
            "success": True,
            "message": "Autenticação efetuada com sucesso.",
            "user": {
                "uid": uid,
                "email": email,
                "name": name,
            },
        })

    except Exception as erro:
        logger.exception(
            "Erro na autenticação Firebase: %s",
            erro,
        )

        return jsonify({
            "success": False,
            "error": (
                "Não foi possível validar "
                "a autenticação Firebase."
            ),
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
    methods=["POST"],
)
def chat():
    if not exigir_login():
        return jsonify({
            "success": False,
            "error": "Não autenticado.",
        }), 401

    if not OPENROUTER_API_KEY:
        return jsonify({
            "success": False,
            "error": (
                "OPENROUTER_API_KEY não está configurada."
            ),
        }), 500

    dados = request.get_json(
        silent=True
    )

    if not dados:
        return jsonify({
            "success": False,
            "error": "Dados inválidos.",
        }), 400

    mensagem = str(
        dados.get(
            "message",
            "",
        )
    ).strip()

    historico = dados.get(
        "history",
        [],
    )

    if not mensagem:
        return jsonify({
            "success": False,
            "error": "Mensagem vazia.",
        }), 400

    # --------------------------------------------------------
    # SISTEMA DA MELLO IA
    # --------------------------------------------------------

    mensagens = [
        {
            "role": "system",
            "content": (
                "Tu és a Mello IA, uma assistente "
                "inteligente desenvolvida pelo "
                "Eng. Ivanildo João Paulo Augusto. "
                "Responde sempre em português. "
                "Sê clara, natural, profissional, "
                "objetiva e útil. "
                "Para perguntas simples, responde "
                "diretamente. "
                "Para estudos, explica passo a passo. "
                "Para matemática, mostra os cálculos. "
                "Para programação, fornece código correto "
                "e explica de forma breve. "
                "Não inventes informações. "
                "Se não souberes algo, diz claramente."
            ),
        }
    ]

    # --------------------------------------------------------
    # HISTÓRICO
    # --------------------------------------------------------

    if isinstance(historico, list):
        for item in historico[-6:]:
            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = item.get("content")

            if role not in (
                "user",
                "assistant",
            ):
                continue

            if not isinstance(content, str):
                continue

            content = content.strip()

            if not content:
                continue

            mensagens.append({
                "role": role,
                "content": content[:2000],
            })

    # --------------------------------------------------------
    # PERGUNTA ATUAL
    # --------------------------------------------------------

    mensagens.append({
        "role": "user",
        "content": mensagem[:4000],
    })

    # --------------------------------------------------------
    # HEADERS
    # --------------------------------------------------------

    headers = {
        "Authorization": (
            f"Bearer {OPENROUTER_API_KEY}"
        ),
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv(
            "APP_URL",
            "http://localhost:5000",
        ),
        "X-Title": "Mello IA",
    }

    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": mensagens,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": False,
    }

    logger.info(
        "Pedido de texto recebido."
    )

    logger.info(
        "Enviando pedido de texto para %s",
        payload["model"],
    )

    logger.info(
        "Max tokens enviados: %s",
        payload["max_tokens"],
    )

    # --------------------------------------------------------
    # OPENROUTER
    # --------------------------------------------------------

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
            "success": False,
            "error": (
                "A OpenRouter demorou demasiado "
                "para responder."
            ),
        }), 504

    except requests.exceptions.RequestException as erro:
        logger.exception(
            "Erro de conexão com OpenRouter: %s",
            erro,
        )

        return jsonify({
            "success": False,
            "error": (
                "Não foi possível conectar "
                "à OpenRouter."
            ),
        }), 502

    logger.info(
        "OpenRouter respondeu HTTP %s",
        resposta.status_code,
    )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:
        resultado = resposta.json()

    except ValueError:
        logger.error(
            "OpenRouter devolveu resposta não-JSON."
        )

        return jsonify({
            "success": False,
            "error": (
                "A OpenRouter devolveu "
                "uma resposta inválida."
            ),
        }), 502

    # --------------------------------------------------------
    # ERRO OPENROUTER
    # --------------------------------------------------------

    if not resposta.ok:
        logger.error(
            "Erro OpenRouter: %s",
            resultado,
        )

        erro = resultado.get(
            "error",
            {},
        )

        if isinstance(erro, dict):
            mensagem_erro = (
                erro.get("message")
                or erro.get("code")
                or "Erro desconhecido da OpenRouter."
            )
        else:
            mensagem_erro = str(
                erro
            )

        erro_lower = str(
            mensagem_erro
        ).lower()

        if (
            resposta.status_code == 402
            or "credit" in erro_lower
            or "credits" in erro_lower
            or "afford" in erro_lower
        ):
            return jsonify({
                "success": False,
                "error": (
                    "A OpenRouter recusou a requisição "
                    "por limite de créditos ou capacidade "
                    "da chave."
                ),
            }), 402

        if (
            "model" in erro_lower
            and (
                "not found" in erro_lower
                or "unavailable" in erro_lower
            )
        ):
            return jsonify({
                "success": False,
                "error": (
                    "O modelo configurado "
                    "não está disponível."
                ),
            }), 503

        return jsonify({
            "success": False,
            "error": (
                f"OpenRouter: {mensagem_erro}"
            ),
        }), resposta.status_code

    # --------------------------------------------------------
    # CHOICES
    # --------------------------------------------------------

    choices = resultado.get(
        "choices",
        [],
    )

    if not choices:
        logger.error(
            "Resposta sem choices: %s",
            resultado,
        )

        return jsonify({
            "success": False,
            "error": (
                "A Mello IA não recebeu "
                "uma resposta do modelo."
            ),
        }), 500

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    message = choices[0].get(
        "message",
        {},
    )

    texto = message.get(
        "content",
        "",
    )

    if isinstance(texto, list):
        partes = []

        for parte in texto:
            if not isinstance(parte, dict):
                continue

            if parte.get("type") == "text":
                partes.append(
                    str(
                        parte.get(
                            "text",
                            "",
                        )
                    )
                )

        texto = "\n".join(
            partes
        )

    texto = str(
        texto or ""
    ).strip()

    if not texto:
        texto = (
            "Recebi a tua pergunta, "
            "mas o modelo não devolveu texto."
        )

    logger.info(
        "Resposta gerada com sucesso."
    )

    return jsonify({
        "success": True,
        "reply": texto,
        "response": texto,
    })


# ============================================================
# API DO UTILIZADOR
# ============================================================

@app.route("/api/me")
def api_me():
    usuario = usuario_atual()

    if not usuario:
        return jsonify({
            "authenticated": False,
        }), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "uid": usuario.uid,
            "email": usuario.email or "",
            "name": (
                usuario.display_name
                or session.get(
                    "name",
                    "",
                )
            ),
        },
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
        "max_tokens": MAX_TOKENS,
    })


# ============================================================
# EXECUÇÃO LOCAL
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
        "OK" if FIREBASE_OK else "ERRO",
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
