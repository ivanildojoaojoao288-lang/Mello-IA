import os
import asyncio
import logging

import edge_tts
import pygame

from dotenv import load_dotenv
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


# ============================================================
# MELLO IA
# ============================================================

class MelloAssistant:

    def __init__(self):

        self.voice = "pt-PT-DuarteNeural"

        api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "OPENROUTER_API_KEY não encontrada no arquivo .env"
            )

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        pygame.mixer.init()

    # ========================================================
    # IDENTIDADE
    # ========================================================

    def get_identity(self):

        return (
            "Eu sou a Mello IA, desenvolvida "
            "pelo Eng. Ivanildo João Paulo Augusto."
        )

    # ========================================================
    # VOZ
    # ========================================================

    async def speak(self, text):

        try:

            logger.info(
                "Gerando áudio..."
            )

            communicate = edge_tts.Communicate(
                text,
                self.voice
            )

            await communicate.save(
                "output.mp3"
            )

            pygame.mixer.music.load(
                "output.mp3"
            )

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():

                await asyncio.sleep(
                    0.1
                )

        except Exception as erro:

            logger.error(
                "Erro na síntese de voz: %s",
                erro
            )

    # ========================================================
    # IA
    # ========================================================

    def get_ai_response(self, prompt):

        texto = prompt.lower()

        if (
            "ivanildo" in texto
            or "quem és" in texto
            or "quem é você" in texto
        ):

            return self.get_identity()

        try:

            completion = (
                self.client
                .chat
                .completions
                .create(

                    model=os.getenv(
                        "OPENROUTER_MODEL",
                        "meta-llama/llama-3.1-8b-instruct"
                    ),

                    messages=[

                        {
                            "role": "system",

                            "content": """
Tu és a Mello IA.

Foste desenvolvida pelo
Eng. Ivanildo João Paulo Augusto.

Responde em português.

Sê clara, natural,
profissional e útil.

Não inventes informações.

Quando explicares uma matéria,
explica passo a passo.

Quando for programação,
fornece código correto e explica
como executar.
                        },

                        {
                            "role": "user",
                            "content": prompt
                        }

                    ],

                    max_tokens=500,

                    temperature=0.7
                )
            )

            if not completion.choices:

                return (
                    "Não consegui gerar uma resposta."
                )

            return (
                completion
                .choices[0]
                .message
                .content
            )

        except Exception as erro:

            logger.error(
                "Erro OpenRouter: %s",
                erro
            )

            return (
                "Não consegui comunicar com "
                "o servidor da Mello IA."
            )

    # ========================================================
    # EXECUTAR
    # ========================================================

    async def run(self):

        logger.info(
            "Mello IA iniciada."
        )

        print(
            "\n===================================="
        )

        print(
            "       MELLO IA"
        )

        print(
            "===================================="
        )

        print(
            "Digite 'sair' para terminar.\n"
        )

        while True:

            try:

                user_input = input(
                    "👤 Tu: "
                ).strip()

                if not user_input:

                    continue

                if user_input.lower() in [
                    "sair",
                    "exit",
                    "quit"
                ]:

                    await self.speak(
                        "Desligando a Mello IA. Até logo."
                    )

                    break

                response = self.get_ai_response(
                    user_input
                )

                print(
                    f"\n🤖 Mello IA: {response}\n"
                )

                await self.speak(
                    response
                )

            except KeyboardInterrupt:

                print(
                    "\nSistema encerrado."
                )

                break

            except Exception as erro:

                logger.error(
                    "Erro: %s",
                    erro
                )


# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":

    assistant = MelloAssistant()

    asyncio.run(
        assistant.run()
    )
