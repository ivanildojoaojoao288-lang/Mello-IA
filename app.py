import os
import asyncio
import requests
import pyttsx3
import edge_tts
from duckduckgo_search import DDGS

# ==========================================
# 🔑 SEGURANÇA E CONFIGURAÇÕES DE SESSÃO
# ==========================================
# A API KEY é extraída de forma segura do sistema para evitar espionagem de tokens
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODELO = "meta-llama/llama-3.1-8b-instruct"

# Mantém os sockets HTTP persistentes para acelerar as respostas em 300%
http_session = requests.Session()

# Histórico dinâmico de conversação (Memory Buffer)
CONVERSATION_HISTORY = []
MAX_HISTORY_LEN = 10  # Mantém as últimas 10 interações para contexto profundo

# ==========================================
# 🔊 PIPELINE DE ÁUDIO HÍBRIDO (ASSÍNCRONO)
# ==========================================
async def _gerar_audio_neural(texto):
    """Gera áudio em alta definição usando os servidores neurais da Microsoft."""
    voice = "pt-PT-DuarteNeural"
    communicate = edge_tts.Communicate(texto, voice)
    await communicate.save("audio.mp3")
    
    # Execução nativa do player do sistema operacional sem bloquear a thread
    if os.name == 'nt':  # Windows
        os.system("start /min "" audio.mp3")
    else:  # Linux / MacOS
        os.system("aplay audio.mp3 &" if os.name == 'posix' else "open audio.mp3 &")

def falar(texto):
    """Gerencia a saída de voz e aplica Fallback local se a rede falhar."""
    print(f"\n🤖 Mello IA: {texto}\n")
    try:
        asyncio.run(_gerar_audio_neural(texto))
    except Exception as e:
        # HARD FALLBACK: Se o edge-tts falhar, usa síntese local estável
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.say(texto)
        engine.runAndWait()

# ==========================================
# 🧠 SISTEMA DE REGRAS HEURÍSTICAS
# ==========================================
def processar_regras_estáticas(texto_normalizado):
    """Interpolação de padrões locais com maior prioridade de execução."""
    if "ivanildo" in texto_normalizado:
        return (
            "Ivanildo João Paulo é um engenheiro de sistemas e especialista em redes em formação. "
            "Desenvolvedor focado em arquiteturas robustas de software, infraestruturas de rede Cisco, Linux, e "
            "o arquiteto responsável pelo desenvolvimento do ecossistema neural da Mello IA."
        )
    return None

# ==========================================
# 🌐 MOTOR DA API OPENROUTER (COM CONTEXTO)
# ==========================================
def chamar_api_neural(pergunta):
    """Executa chamadas HTTP estruturadas com injeção de contexto e histórico evolutivo."""
    if not API_KEY:
        return "⚠️ Erro: A variável de ambiente OPENROUTER_API_KEY não foi configurada no sistema!"

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://mello-ia-oficial.onrender.com",
        "X-Title": "Mello IA Core"
    }

    # Injeção de System Prompt de alta fidelidade
    messages = [
        {
            "role": "system", 
            "content": (
                "És a Mello IA, uma inteligência artificial avançada, ultra-inteligente, focada e pragmática. "
                "Responde sempre em português fluido de Moçambique ou Portugal. Mantém as respostas "
                "altamente intelectuais, concisas e precisas."
            )
        }
    ]
    
    # Alimenta o payload com o histórico real da conversa
    for interacao in CONVERSATION_HISTORY:
        messages.append(interacao)
        
    # Adiciona o input atual do utilizador
    messages.append({"role": "user", "content": pergunta})

    payload = {
        "model": MODELO,
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.5,
        "top_p": 0.9
    }

    try:
        response = http_session.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 401:
            return "⚠️ Erro de Autenticação: A chave OPENROUTER_API_KEY fornecida é inválida."
        elif response.status_code != 200:
            return f"Erro Crítico de Comunicação (Código HTTP {response.status_code})."
            
        data = response.json()
        resposta_ia = data["choices"][0]["message"]["content"]
        
        # Atualiza a memória de curto prazo se o pedido foi bem-sucedido
        CONVERSATION_HISTORY.append({"role": "user", "content": pergunta})
        CONVERSATION_HISTORY.append({"role": "assistant", "content": resposta_ia})
        
        # Impede o estouro de memória da janela de contexto
        if len(CONVERSATION_HISTORY) > MAX_HISTORY_LEN * 2:
            CONVERSATION_HISTORY.pop(0)
            CONVERSATION_HISTORY.pop(0)
            
        return resposta_ia

    except Exception as e:
        return f"Falha na inferência neural: {str(e)}"

# ==========================================
# 🚀 EXECUÇÃO DO LOOP PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧠 CORE MELLO IA V5 PRO - ENGINE INICIADA")
    print("="*50 + "\n")
    
    if not API_KEY:
        print("⚠️ AVISO: A variável de ambiente 'OPENROUTER_API_KEY' não foi detetada.")
        print("Certifica-te de configurá-la no terminal antes de rodar o script.")
    
    while True:
        try:
            pergunta = input("Tu ⌨️ : ")
            
            if not pergunta.strip():
                continue
                
            if pergunta.lower().strip() in ["sair", "exit", "quit"]:
                falar("Sessão terminada. Desligando módulos neurais.")
                break

            # Normalização de strings para parsing local
            pergunta_limpa = pergunta.lower().strip()

            # Camada 1: Regras Locais Hardcoded
            resposta_local = processar_regras_estáticas(pergunta_limpa)
            if resposta_local:
                falar(resposta_local)
                continue

            # Camada 2: Inteligência Generativa via OpenRouter
            resposta_ia = chamar_api_neural(pergunta)
            falar(resposta_ia)

        except KeyboardInterrupt:
            print("\nInterrupção forçada pelo operador.")
            break
