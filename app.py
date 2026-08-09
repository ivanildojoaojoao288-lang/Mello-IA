import os
import base64
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv


# =====================================================
# CONFIGURAÇÃO
# =====================================================

load_dotenv()

app = Flask(__name__)
CORS(app)


API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# =====================================================
# PROMPT PRINCIPAL
# =====================================================

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna,
profissional e amigável.

Foste desenvolvida pelo Eng. Ivanildo João Paulo Augusto.

Características:

- Responde em português.
- Usa linguagem clara e simples.
- Sê técnica quando necessário.
- Ajuda em programação, informática, redes, matemática,
  estudos, tecnologia e informação geral.
- Quando receberes uma imagem, analisa cuidadosamente
  o conteúdo visível.
- Podes explicar textos presentes na imagem.
- Podes resolver exercícios matemáticos presentes na imagem.
- Podes interpretar tabelas, códigos, diagramas,
  documentos e fotografias.
- Não inventes informações que não estejam disponíveis.
- Se uma parte da imagem estiver ilegível, informa isso.
- Em cálculos, mostra o raciocínio e apresenta o resultado
  de forma organizada.
- Nunca reveles chaves API, configurações internas ou
  informações secretas do servidor.

Quando perguntarem quem criou a Mello IA, responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João Paulo
Augusto, com foco em inteligência artificial, programação
e inovação tecnológica."
"""


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

@app.route("/")
def inicio():
    return render_template("chat.html")


# =====================================================
# FUNÇÃO PARA CONVERTER IMAGEM EM BASE64
# =====================================================

def imagem_para_data_url(arquivo):
    """
    Converte a imagem enviada pelo navegador
    para Data URL Base64.
    """

    dados = arquivo.read()

    if not dados:
        raise ValueError("A imagem enviada está vazia.")

    mime_type = arquivo.mimetype or "image/jpeg"

    base64_imagem = base64.b64encode(dados).decode("utf-8")

    return f"data:{mime_type};base64,{base64_imagem}"


# =====================================================
# CHAMAR OPENROUTER
# =====================================================

def chamar_openrouter(mensagem, imagem=None):

    if not API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY não está configurada."
        )

    # -------------------------------------------------
    # SEM IMAGEM
    # -------------------------------------------------

    if imagem is None:

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

            "temperature": 0.7
        }

    # -------------------------------------------------
    # COM IMAGEM
    # -------------------------------------------------

    else:

        imagem_url = imagem_para_data_url(imagem)

        conteudo = []

        if mensagem:
            conteudo.append({
                "type": "text",
                "text": mensagem
            })
        else:
            conteudo.append({
                "type": "text",
                "text": (
                    "Analisa esta imagem cuidadosamente. "
                    "Descreve o que está presente e responde "
                    "ao que for possível identificar."
                )
            })

        conteudo.append({
            "type": "image_url",
            "image_url": {
                "url": imagem_url
            }
        })

        payload = {
            "model": VISION_MODEL,

            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": conteudo
                }
            ],

            "temperature": 0.4
        }

    # -------------------------------------------------
    # PEDIDO
    # -------------------------------------------------

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    resposta = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    print("STATUS OPENROUTER:", resposta.status_code)

    try:
        resultado = resposta.json()
    except Exception:
        raise ValueError(
            f"OpenRouter devolveu uma resposta inválida: "
            f"{resposta.text[:500]}"
        )

    print("RESPOSTA OPENROUTER:")
    print(resultado)

    # -------------------------------------------------
    # ERRO DA API
    # -------------------------------------------------

    if resposta.status_code != 200:

        erro = resultado.get("error", {})

        mensagem_erro = (
            erro.get("message")
            if isinstance(erro, dict)
            else str(erro)
        )

        raise ValueError(
            mensagem_erro or
            "Erro desconhecido na comunicação com o OpenRouter."
        )

    # -------------------------------------------------
    # VALIDAR RESPOSTA
    # -------------------------------------------------

    choices = resultado.get("choices")

    if not choices:
        raise ValueError(
            "A IA não devolveu nenhuma resposta."
        )

    mensagem_resultado = choices[0].get("message", {})

    texto = mensagem_resultado.get("content")

    if not texto:
        raise ValueError(
            "A IA devolveu uma resposta vazia."
        )

    return texto


# =====================================================
# CHAT
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        # =================================================
        # TEXTO
        # =================================================

        mensagem = request.form.get(
            "message",
            ""
        ).strip()


        # =================================================
        # IMAGEM
        # =================================================

        imagem = request.files.get("image")


        # =================================================
        # VALIDAR
        # =================================================

        if not mensagem and not imagem:

            return jsonify({
                "reply": "Escreva uma mensagem ou envie uma imagem."
            }), 400


        # =================================================
        # VALIDAR IMAGEM
        # =================================================

        if imagem:

            if not imagem.mimetype:

                return jsonify({
                    "reply": "Não foi possível identificar o tipo da imagem."
                }), 400


            if not imagem.mimetype.startswith("image/"):

                return jsonify({
                    "reply": "O ficheiro enviado não é uma imagem válida."
                }), 400


            # Limite de 10 MB
            imagem.seek(0, 2)

            tamanho = imagem.tell()

            imagem.seek(0)


            if tamanho > 10 * 1024 * 1024:

                return jsonify({
                    "reply": "A imagem deve ter no máximo 10 MB."
                }), 400


        # =================================================
        # PROCESSAR
        # =================================================

        print("\n======================================")
        print("📨 NOVA SOLICITAÇÃO")
        print("======================================")

        print("Mensagem:", mensagem)

        if imagem:
            print("📷 Imagem:", imagem.filename)
            print("📦 Tipo:", imagem.mimetype)

        if imagem:

            print(
                "🧠 Modelo Vision:",
                VISION_MODEL
            )

        else:

            print(
                "🧠 Modelo:",
                MODEL
            )


        resposta = chamar_openrouter(
            mensagem,
            imagem
        )


        # =================================================
        # RESPOSTA
        # =================================================

        return jsonify({
            "reply": resposta
        })


    except requests.exceptions.Timeout:

        print("❌ TIMEOUT")

        return jsonify({
            "reply": (
                "A Mello IA demorou demasiado tempo para "
                "responder. Tente novamente."
            )
        }), 504


    except requests.exceptions.RequestException as erro:

        print("❌ ERRO DE CONEXÃO:")
        print(erro)

        return jsonify({
            "reply": (
                "Não foi possível comunicar com o servidor "
                "de inteligência artificial."
            )
        }), 502


    except Exception as erro:

        print("❌ ERRO:")
        print(erro)

        return jsonify({
            "reply": (
                "Ocorreu um erro ao processar o pedido."
            ),
            "detalhes": str(erro)
        }), 500


# =====================================================
# EXECUTAR
# =====================================================

if __name__ == "__main__":

    print("")
    print("==============================================")
    print("🚀 MELLO IA")
    print("==============================================")
    print("🤖 Modelo:", MODEL)
    print("👁️ Vision:", VISION_MODEL)
    print(
        "🔑 API Key:",
        "CARREGADA" if API_KEY else "NÃO CONFIGURADA"
    )
    print("==============================================")
    print("🌐 http://127.0.0.1:5000")
    print("==============================================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
