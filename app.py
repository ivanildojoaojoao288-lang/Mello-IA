import os
import asyncio
import logging
import edge_tts
import pygame
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI # Recomendado usar a lib oficial do OpenRouter

# Configuração de Logs Profissionais
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

class MelloAssistant:
    def __init__(self):
        self.voice = "pt-PT-DuarteNeural"
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        pygame.mixer.init()

    def _get_identity(self) -> str:
        return (
            "Eu sou a Mello IA 5 Pro, desenvolvida pelo Engenheiro Ivanildo. "
            "Ivanildo é um estudante de Informática e Engenharia focado em sistemas, "
            "inteligência artificial e automação. Sou seu sistema de suporte técnico "
            "de alta performance."
        )

    async def speak(self, text: str):
        try:
            logger.info(f"Gerando áudio: {text}")
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save("output.mp3")
            
            pygame.mixer.music.load("output.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Erro na síntese de voz: {e}")

    def get_ai_response(self, prompt: str) -> str:
        if any(keyword in prompt.lower() for keyword in ["ivanildo", "quem és"]):
            return self._get_identity()
            
        try:
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct",
                messages=[
                    {"role": "system", "content": "Seja técnico, direto e profissional."},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro crítico no processamento neural: {str(e)}"

    async def run(self):
        logger.info("Sistema Mello IA 5 Pro Inicializado com Sucesso.")
        while True:
            try:
                user_input = input("\n👤 Tu: ")
                if user_input.lower() in ["sair", "exit"]:
                    await self.speak("Desligando sistema. Até logo, Engenheiro.")
                    break
                
                response = self.get_ai_response(user_input)
                print(f"🤖 Mello IA: {response}")
                await self.speak(response)
                
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    assistant = MelloAssistant()
    asyncio.run(assistant.run())
