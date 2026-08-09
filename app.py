import os
import base64
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# =====================================================
# CONFIGURAÇÃO
# =====================================================

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.1-8b-instruct"
)

VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "google/gemini-2.5-flash"
)

IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "openai/gpt-5-image"
)

print("===================================")
print("MELLO IA")
print("===================================")
print("CHAVE CARREGADA:", bool(API_KEY))
print("MODELO TEXTO:", MODEL)
print("MODELO VISÃO:", VISION_MODEL)
print("MODELO IMAGEM:", IMAGE_MODEL)
print("===================================")


# =====================================================
# PERSONALIDADE DA MELLO IA
# =====================================================

SYSTEM_PROMPT = """
Tu és a Mello IA, uma assistente inteligente moderna,
profissional e amigável.

Responde em português claro.

És capaz de ajudar em:

- programação
- tecnologia
- redes de computadores
- informática
- matemática
- estudos
- trabalhos académicos
- análise de imagens
- leitura de textos em fotografias
- interpretação de exercícios fotografados
- resolução de contas
- explicação de gráficos, tabelas e documentos

Quando receberes uma imagem:

1. Analisa cuidadosamente a imagem.
2. Identifica textos, números, símbolos, tabelas,
   gráficos ou exercícios.
3. Responde exatamente ao que foi solicitado.
4. Se for uma conta matemática, mostra o cálculo
   passo a passo.
5. Se houver informação ilegível, informa claramente
   qual parte não foi possível identificar.
6. Não inventes informações que não estejam visíveis.

Quando perguntarem:

"Quem criou a Mello IA?"

Responde:

"A Mello IA foi desenvolvida pelo Eng. Ivanildo João
Paulo Augusto, com foco em inteligência artificial,
programação e inovação tecnológica."
"""


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

@app.route("/")
def inicio():
    return render_template("chat.html")


# =====================================================
# CHAT
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    if not API_KEY:
        return jsonify({
            "reply": "A chave da API não está configurada no servidor."
        }), 500

    try:

        # =================================================
        # RECEBER DADOS
        # =================================================

        mensagem = request.form.get("message", "").strip()

        imagem = request.files.get("image")


        # =================================================
        # SEM TEXTO E SEM IMAGEM
        # =================================================

        if not mensagem and not imagem:
            return jsonify({
                "reply": "Escreva uma mensagem ou envie uma imagem."
            }), 400


        # =================================================
        # ANALISAR IMAGEM
        # =================================================

        if imagem:

            print("📷 Imagem recebida:")
            print(imagem.filename)
            print(imagem.mimetype)


            # Verificar formato
            formatos_permitidos = [
                "image/jpeg",
                "image/png",
                "image/webp",
                "image/gif"
            ]

            if imagem.mimetype not in formatos_permitidos:

                return jsonify({
                    "reply":
                    "Formato de imagem não suportado. "
                    "Use JPG, PNG, WEBP ou GIF."
                }), 400


            # Ler imagem
            dados_imagem = imagem.read()


            if not dados_imagem:

                return jsonify({
                    "reply": "Não foi possível ler a imagem."
                }), 400


            # Converter para Base64
            imagem_base64 = base64.b64encode(
                dados_imagem
            ).decode("utf-8")


            # Data URL
            imagem_url = (
                f"data:{imagem.mimetype};base64,"
                f"{imagem_base64}"
            )


            # Se não escreveu nada,
            # usar uma pergunta padrão
            if not mensagem:

                mensagem = (
                    "Analise esta imagem cuidadosamente. "
                    "Explique tudo o que está nela. "
                    "Se houver uma conta ou exercício, "
                    "resolva passo a passo."
                )


            # =================================================
            # REQUEST VISION
            # =================================================

            payload = {

                "model": VISION_MODEL,

                "messages": [

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },

                    {
                        "role": "user",

                        "content": [

                            {
                                "type": "text",
                                "text": mensagem
                            },

                            {
                                "type": "image_url",

                                "image_url": {
                                    "url": imagem_url
                                }
                            }

                        ]
                    }

                ],

                "temperature": 0.4
            }


            print("🔎 Enviando imagem para:", VISION_MODEL)


        # =================================================
        # CHAT NORMAL
        # =================================================

        else:

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


            print("💬 Enviando texto para:", MODEL)


        # =================================================
        # OPENROUTER
        # =================================================

        resposta = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json=payload,

            timeout=120
        )


        print("STATUS OPENROUTER:", resposta.status_code)


        # =================================================
        # LER RESPOSTA
        # =================================================

        try:

            resultado = resposta.json()

        except Exception:

            return jsonify({
                "reply":
                "O servidor da IA devolveu uma resposta inválida."
            }), 500


        print("RESPOSTA OPENROUTER:")
        print(resultado)


        # =================================================
        # ERRO OPENROUTER
        # =================================================

        if resposta.status_code != 200:

            erro = resultado.get(
                "error",
                {}
            )

            mensagem_erro = erro.get(
                "message",
                "Erro desconhecido na comunicação com a IA."
            )

            return jsonify({
                "reply": mensagem_erro
            }), resposta.status_code


        # =================================================
        # EXTRAIR RESPOSTA
        # =================================================

        choices = resultado.get("choices")

        if not choices:

            return jsonify({
                "reply":
                "A IA não devolveu nenhuma resposta."
            }), 500


        texto = choices[0]["message"]["content"]


        # =================================================
        # RESPONDER AO FRONTEND
        # =================================================

        return jsonify({
            "reply": texto
        })


    except requests.exceptions.Timeout:

        print("⏱️ Timeout")

        return jsonify({
            "reply":
            "A Mello IA demorou demasiado tempo para responder. "
            "Tente novamente."
        }), 504


    except Exception as erro:

        print("❌ ERRO:")
        print(erro)

        return jsonify({
            "reply":
            "Erro interno da Mello IA.",
            "detalhes": str(erro)
        }), 500


# =====================================================
# INICIAR
# =====================================================

if __name__ == "__main__":

    print("🚀 Mello IA online")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
