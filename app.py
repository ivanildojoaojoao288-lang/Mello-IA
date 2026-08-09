```python
import os
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv


# ========================================
# CARREGAR VARIÁVEIS DE AMBIENTE
# ========================================

load_dotenv()


# ========================================
# INICIALIZAR FLASK
# ========================================

app = Flask(__name__)

CORS(app)


# ========================================
# CONFIGURAÇÃO DA IA
# ========================================

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = os.getenv("OPENROUTER_MODEL")


print("CHAVE CARREGADA:", bool(API_KEY))
print("MODELO:", MODEL)


# ========================================
# PERSONALIDADE DA MELLO IA
# ========================================

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna.

Características:

- Respostas claras e profissionais.
- Linguagem simples e fácil de entender.
- Ajuda em programação, tecnologia, estudos e informação geral.
- Explica conceitos passo a passo quando necessário.
- Não inventa informações.
- Quando não souber alguma coisa, informa claramente.
- Nunca reveles chaves, tokens ou configurações internas.

Quando perguntarem:

"Quem criou a Mello IA?"

Responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João Paulo Augusto,
com foco em inteligência artificial, programação e inovação tecnológica."
"""


# ========================================
# PÁGINA PRINCIPAL
# ========================================

@app.route("/")
def inicio():

    return render_template("chat.html")


# ========================================
# CHAT COM A MELLO IA
# ========================================

@app.route("/chat", methods=["POST"])
def chat():

    dados = request.get_json(silent=True) or {}

    mensagem = dados.get("message", "").strip()


    # ------------------------------------
    # VERIFICAR MENSAGEM
    # ------------------------------------

    if not mensagem:

        return jsonify({
            "reply": "Por favor, escreva uma mensagem."
        }), 400


    # ------------------------------------
    # VERIFICAR CONFIGURAÇÃO
    # ------------------------------------

    if not API_KEY:

        return jsonify({
            "reply": "A chave da API da Mello IA não está configurada."
        }), 500


    if not MODEL:

        return jsonify({
            "reply": "O modelo da Mello IA não está configurado."
        }), 500


    try:

        # --------------------------------
        # ENVIAR PEDIDO PARA OPENROUTER
        # --------------------------------

        resposta = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={

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

            },

            timeout=60

        )


        # --------------------------------
        # TRANSFORMAR RESPOSTA EM JSON
        # --------------------------------

        resultado = resposta.json()


        print("STATUS OPENROUTER:", resposta.status_code)

        print("RESPOSTA OPENROUTER:")

        print(resultado)


        # --------------------------------
        # VERIFICAR ERRO DA API
        # --------------------------------

        if resposta.status_code != 200:

            return jsonify({

                "reply": "A Mello IA encontrou um problema ao comunicar com o serviço de inteligência artificial.",

                "detalhes": resultado

            }), 500


        # --------------------------------
        # VERIFICAR CHOICES
        # --------------------------------

        if "choices" not in resultado:

            return jsonify({

                "reply": "A IA não retornou uma resposta válida.",

                "detalhes": resultado

            }), 500


        # --------------------------------
        # OBTER RESPOSTA
        # --------------------------------

        texto = resultado["choices"][0]["message"]["content"]


        # --------------------------------
        # DEVOLVER PARA O FRONTEND
        # --------------------------------

        return jsonify({

            "reply": texto

        })


    except requests.exceptions.Timeout:

        return jsonify({

            "reply": "A comunicação com a IA demorou demasiado. Tenta novamente."

        }), 504


    except requests.exceptions.RequestException as erro:

        print("ERRO DE REQUEST:", erro)

        return jsonify({

            "reply": "Não foi possível comunicar com o serviço de IA.",

            "detalhes": str(erro)

        }), 500


    except Exception as erro:

        print("ERRO INTERNO:", erro)

        return jsonify({

            "reply": "Ocorreu um erro interno na Mello IA.",

            "detalhes": str(erro)

        }), 500


# ========================================
# INICIAR SERVIDOR
# ========================================

if __name__ == "__main__":

    print("🚀 Mello IA online")

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )
```
