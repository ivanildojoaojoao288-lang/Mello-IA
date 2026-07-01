import os
import asyncio
import edge_tts
import requests
from duckduckgo_search import DDGS

# CONFIGURAÇÃO DE IDENTIDADE
API_KEY = os.getenv("OPENROUTER_API_KEY") # Recomendado: Guardar no sistema
VOICE = "pt-PT-DuarteNeural"

# =========================
# 🔊 VOZ NATURAL (Async)
# =========================
async def falar_async(texto):
    communicate = edge_tts.Communicate(texto, VOICE)
    await communicate.save("audio.mp3")
    os.system("start audio.mp3")

def falar(texto):
    print(f"IA: {texto}")
    asyncio.run(falar_async(texto))

# =========================
# 📌 REGRAS FIXAS (Identidade)
# =========================
def regras(texto):
    texto_limpo = texto.lower()
    if "ivanildo" in texto_limpo or "quem és" in texto_limpo:
        return (
            "Eu sou a Mello IA 5 Pro, desenvolvida pelo Engenheiro Ivanildo. "
            "Ivanildo é um estudante de Informática e Engenharia focado em sistemas, "
            "inteligência artificial e automação. Sou o seu sistema de suporte técnico "
            "de alta performance."
        )
    return None

# =========================
# 🌐 MOTOR DE IA
# =========================
def chamar_api(pergunta):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3.1-8b-instruct",
                "messages": [
                    {"role": "system", "content": "Responde de forma técnica, direta e profissional em português."},
                    {"role": "user", "content": pergunta}
                ]
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro de conexão: {e}"

# =========================
# 🚀 LOOP PRINCIPAL
# =========================
def main():
    print("--- Mello IA 5 Pro Inicializada ---")
    while True:
        try:
            pergunta = input("Tu: ")
            if pergunta.lower() == "sair":
                falar("Até logo, Engenheiro.")
                break

            # 1. Prioridade às Regras Fixas
            resposta = regras(pergunta)
            
            # 2. Se não for regra, consulta a IA
            if not resposta:
                resposta = chamar_api(pergunta)
            
            falar(resposta)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
