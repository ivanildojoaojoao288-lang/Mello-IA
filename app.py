import os
import asyncio
import edge_tts
import requests
from playsound import playsound

# CONFIGURAÇÃO
API_KEY = os.getenv("OPENROUTER_API_KEY")
VOICE = "pt-PT-DuarteNeural"
AUDIO_FILE = "audio.mp3"

# =========================
# 🔊 VOZ NATURAL
# =========================
async def gerar_audio(texto):
    """Gera o arquivo de áudio e reproduz."""
    communicate = edge_tts.Communicate(texto, VOICE)
    await communicate.save(AUDIO_FILE)
    # Toca o áudio (o playsound é compatível com Windows/Mac/Linux)
    playsound(AUDIO_FILE)

def falar(texto):
    print(f"IA: {texto}")
    # Executa a função assíncrona de forma síncrona para o loop principal
    asyncio.run(gerar_audio(texto))

# =========================
# 📌 REGRAS E IA
# =========================
def responder(pergunta):
    # Regras fixas (Identidade)
    if any(palavra in pergunta.lower() for palavra in ["ivanildo", "quem és"]):
        return ("Eu sou a Mello IA 5 Pro, desenvolvida pelo Engenheiro Ivanildo. "
                "Sou o seu sistema de suporte técnico de alta performance.")
    
    # Consulta API (OpenRouter)
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "meta-llama/llama-3.1-8b-instruct",
                "messages": [
                    {"role": "system", "content": "Responde de forma técnica e profissional em português."},
                    {"role": "user", "content": pergunta}
                ]
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro na conexão com a IA: {e}"

# =========================
# 🚀 LOOP PRINCIPAL
# =========================
def main():
    print("--- Mello IA 5 Pro Inicializada ---")
    while True:
        try:
            pergunta = input("Tu: ")
            if pergunta.lower() in ["sair", "exit"]:
                falar("Até logo, Engenheiro.")
                break

            resposta = responder(pergunta)
            falar(resposta)
            
        except KeyboardInterrupt:
            print("\nEncerrando sistema...")
            break

if __name__ == "__main__":
    main()
