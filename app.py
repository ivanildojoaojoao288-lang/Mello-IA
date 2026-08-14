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
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


# ============================================================
# TOKENS
# ============================================================

# A Mello tenta primeiro responder com até 2000 tokens.
MAX_TOKENS = 2000

# Se a chave não conseguir suportar 2000,
# tenta automaticamente estes limites.
TOKEN_FALLBACKS = [600, 300]


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
# STATUS
# ============================================================

if OPENROUTER_API_KEY:

    logger.info(
        "OpenRouter configurado."
    )

else:

    logger.warning(
        "OPENROUTER_API_KEY não encontrada."
    )


# ============================================================
# UTILIZADOR
# ============================================================

def usuario_atual():

    uid = session.get(
        "firebase_uid"
    )

    if not uid:

        return None

    try:

        return auth.get_user(uid)

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

                "uid":
                    uid,

                "email":
                    email,

                "name":
                    name

            }

        })


    except Exception as erro:

        logger.exception(
            "Erro na autenticação Firebase: %s",
            erro
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
# FUNÇÃO PARA IDENTIFICAR ERRO DE CAPACIDADE
# ============================================================

def erro_eh_limite_tokens(
    status_code,
    mensagem
):

    texto = str(
        mensagem or ""
    ).lower()


    palavras = [

        "credit",
        "credits",
        "afford",
        "max_tokens",
        "tokens",
        "limit",
        "capacity"

    ]


    if status_code == 402:

        return True


    return any(
        palavra in texto
        for palavra in palavras
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
    # LOGIN
    # --------------------------------------------------------

    if not exigir_login():

        return jsonify({

            "success": False,

            "error":
                "Não autenticado."

        }), 401


    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    if not OPENROUTER_API_KEY:

        return jsonify({

            "success": False,

            "error":
                "OPENROUTER_API_KEY não configurada."

        }), 500


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


    historico = dados.get(
        "history",
        []
    )


    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    if not mensagem:

        return jsonify({

            "success": False,

            "error":
                "Mensagem vazia."

        }), 400


    # ========================================================
    # SISTEMA DA MELLO IA
    # ========================================================

    sistema = (

        "Tu és a Mello IA, uma assistente "
        "inteligente desenvolvida pelo "
        "Eng. Ivanildo João Paulo Augusto. "

        "Responde sempre em português. "

        "Sê clara, natural, objetiva e útil. "

        "Para perguntas simples, responde "
        "diretamente e de forma curta. "

        "Para questões escolares, apresenta "
        "a resposta e uma explicação simples. "

        "Para matemática, mostra os cálculos "
        "necessários. "

        "Para programação, fornece código correto "
        "e explicação clara. "

        "Quando o utilizador pedir código, "
        "fornece código completo quando necessário. "

        "Não inventes informações. "

        "Se não souberes alguma coisa, "
        "diz claramente que não sabes."

    )


    # ========================================================
    # CONSTRUIR MENSAGENS
    # ========================================================

    mensagens = [

        {
            "role": "system",
            "content": sistema
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

                "role":
                    role,

                "content":
                    content

            })


    # ========================================================
    # PERGUNTA ATUAL
    # ========================================================

    mensagens.append({

        "role":
            "user",

        "content":
            mensagem

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
            "http://localhost:5000",

        "X-Title":
            "Mello IA"

    }


    # ========================================================
    # TENTATIVAS
    # ========================================================

    limites = [

        MAX_TOKENS

    ] + TOKEN_FALLBACKS


    ultima_resposta = None
    ultima_mensagem_erro = ""


    for limite_tokens in limites:

        logger.info(
            "Tentando OpenRouter com %s tokens.",
            limite_tokens
        )


        payload = {

            "model":
                OPENROUTER_MODEL,

            "messages":
                mensagens,

            "max_tokens":
                limite_tokens,

            "temperature":
                0.3,

            "stream":
                False

        }


        # ----------------------------------------------------
        # PEDIDO
        # ----------------------------------------------------

        try:

            resposta_http = requests.post(

                OPENROUTER_URL,

                headers=headers,

                json=payload,

                timeout=90

            )


        except requests.exceptions.Timeout:

            logger.error(
                "Timeout na OpenRouter."
            )

            return jsonify({

                "success": False,

                "error":
                    "A OpenRouter demorou demasiado "
                    "para responder."

            }), 504


        except requests.exceptions.RequestException as erro:

            logger.exception(
                "Erro de conexão: %s",
                erro
            )

            return jsonify({

                "success": False,

                "error":
                    "Não foi possível conectar "
                    "à OpenRouter."

            }), 502


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        logger.info(
            "OpenRouter respondeu HTTP %s.",
            resposta_http.status_code
        )


        # ----------------------------------------------------
        # JSON
        # ----------------------------------------------------

        try:

            resultado = resposta_http.json()


        except ValueError:

            logger.error(
                "Resposta inválida da OpenRouter."
            )

            return jsonify({

                "success": False,

                "error":
                    "A OpenRouter devolveu "
                    "uma resposta inválida."

            }), 502


        # ----------------------------------------------------
        # SE DEU CERTO
        # ----------------------------------------------------

        if resposta_http.ok:

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
                        "A Mello IA não recebeu "
                        "resposta do modelo."

                }), 500


            message = choices[0].get(
                "message",
                {}
            )


            texto = message.get(
                "content",
                ""
            )


            # ------------------------------------------------
            # CONTENT EM LISTA
            # ------------------------------------------------

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


            texto = str(
                texto or ""
            ).strip()


            if not texto:

                texto = (

                    "O modelo recebeu a pergunta, "
                    "mas não devolveu texto."

                )


            logger.info(
                "Resposta gerada com sucesso usando %s tokens.",
                limite_tokens
            )


            return jsonify({

                "success":
                    True,

                "reply":
                    texto,

                "response":
                    texto,

                "tokens_limit":
                    limite_tokens

            })


        # ----------------------------------------------------
        # ERRO
        # ----------------------------------------------------

        erro = resultado.get(
            "error",
            {}
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

                "Erro desconhecido."

            )


        else:

            mensagem_erro = str(
                erro
            )


        ultima_resposta = resposta_http.status_code
        ultima_mensagem_erro = str(
            mensagem_erro
        )


        logger.error(
            "Erro OpenRouter: %s",
            mensagem_erro
        )


        # ----------------------------------------------------
        # FALHA DE TOKEN/CAPACIDADE
        # ----------------------------------------------------

        if erro_eh_limite_tokens(

            resposta_http.status_code,

            mensagem_erro

        ):

            if limite_tokens != limites[-1]:

                logger.warning(

                    "Limite insuficiente para %s tokens. "
                    "Tentando fallback."

                    ,

                    limite_tokens

                )

                continue


        # ----------------------------------------------------
        # ERRO DE AUTENTICAÇÃO
        # ----------------------------------------------------

        if resposta_http.status_code == 401:

            return jsonify({

                "success":
                    False,

                "error":
                    "A chave da OpenRouter é inválida "
                    "ou não foi autorizada."

            }), 401


        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        if resposta_http.status_code == 429:

            return jsonify({

                "success":
                    False,

                "error":
                    "A OpenRouter atingiu o limite "
                    "de requisições. Tenta novamente "
                    "dentro de alguns instantes."

            }), 429


        # ----------------------------------------------------
        # MODELO
        # ----------------------------------------------------

        erro_lower = str(
            mensagem_erro
        ).lower()


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

                "error":
                    "O modelo configurado na OpenRouter "
                    "não está disponível neste momento."

            }), 503


        # ----------------------------------------------------
        # OUTRO ERRO
        # ----------------------------------------------------

        return jsonify({

            "success":
                False,

            "error":
                f"OpenRouter: {mensagem_erro}"

        }), resposta_http.status_code


    # ========================================================
    # TODAS AS TENTATIVAS FALHARAM
    # ========================================================

    return jsonify({

        "success":
            False,

        "error": (

            "A Mello IA tentou responder com "
            f"{MAX_TOKENS}, 600 e 300 tokens, "
            "mas a OpenRouter não autorizou "
            "nenhuma das tentativas. "

            f"Último erro: {ultima_mensagem_erro}"

        ),

        "status":
            ultima_resposta

    }), 402


# ============================================================
# API DO UTILIZADOR
# ============================================================

@app.route("/api/me")
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

@app.route("/health")
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
            MAX_TOKENS,

        "fallbacks":
            TOKEN_FALLBACKS

    })


# ============================================================
# INICIAR
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
        "Max tokens principal: %s",
        MAX_TOKENS
    )

    logger.info(
        "Fallbacks: %s",
        TOKEN_FALLBACKS
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

        debug=False

    )
