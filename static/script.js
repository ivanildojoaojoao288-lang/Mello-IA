// ===============================
// MELLO IA - SCRIPT PRINCIPAL
// ===============================

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");
const welcome = document.getElementById("welcome");

// ===============================
// ENVIAR MENSAGEM
// ===============================

async function enviarMensagem() {

    const mensagem = input.value.trim();

    if (!mensagem) return;

    // Esconder tela inicial
    if (welcome) {
        welcome.style.display = "none";
    }

    // Mostrar mensagem do utilizador
    adicionarMensagem("user", mensagem);

    // Limpar campo
    input.value = "";

    // Ajustar altura
    ajustarTextarea();

    // Desativar botão
    sendButton.disabled = true;

    // Mostrar indicador
    const loading = adicionarLoading();

    try {

        const resposta = await fetch("/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: mensagem
            })
        });

        const data = await resposta.json();

        // Remover indicador
        loading.remove();

        if (!resposta.ok) {

            adicionarMensagem(
                "bot",
                data.reply || "Ocorreu um erro ao processar a mensagem."
            );

            return;
        }

        // Mostrar resposta da IA
        adicionarMensagem(
            "bot",
            data.reply || "Não consegui gerar uma resposta."
        );

        // Guardar conversa no histórico
        adicionarHistorico(mensagem);

    } catch (erro) {

        console.error("Erro:", erro);

        loading.remove();

        adicionarMensagem(
            "bot",
            "Não consegui conectar ao servidor da Mello IA. Verifique se o servidor está online."
        );

    } finally {

        sendButton.disabled = false;

        input.focus();
    }
}


// ===============================
// ADICIONAR MENSAGEM
// ===============================

function adicionarMensagem(tipo, texto) {

    const message = document.createElement("div");

    message.className = `message ${tipo}`;

    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent =
        tipo === "bot" ? "M" : "👤";

    const content = document.createElement("div");

    content.className = "message-content";

    // Evita inserir HTML diretamente vindo da API
    content.textContent = texto;

    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);

    // Scroll automático
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });

    return message;
}


// ===============================
// INDICADOR DE RESPOSTA
// ===============================

function adicionarLoading() {

    const message = document.createElement("div");

    message.className = "message bot";

    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent = "M";

    const content = document.createElement("div");

    content.className = "message-content";

    const loading = document.createElement("div");

    loading.className = "typing";

    loading.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    ;

    content.appendChild(loading);

    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });

    return message;
}


// ===============================
// ENTER PARA ENVIAR
// ===============================

function handleKey(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        enviarMensagem();
    }
}


// ===============================
// TEXTAREA AUTOMÁTICO
// ===============================

input.addEventListener("input", ajustarTextarea);

function ajustarTextarea() {

    input.style.height = "auto";

    input.style.height =
        Math.min(input.scrollHeight, 130) + "px";
}


// ===============================
// SUGESTÕES
// ===============================

function usarSugestao(texto) {

    input.value = texto;

    ajustarTextarea();

    input.focus();

    enviarMensagem();
}


// ===============================
// NOVA CONVERSA
// ===============================

function novaConversa() {

    chatBox.innerHTML = "";

    // Recriar tela inicial
    const novaTela = document.createElement("div");

    novaTela.className = "welcome";

    novaTela.id = "welcome";

    novaTela.innerHTML = `
        <div class="welcome-logo">
            M
        </div>

        <h1>
            Olá! Eu sou a <span>Mello IA</span>
        </h1>

        <p>
            Assistente inteligente de tecnologia,
            programação, estudos e inovação.
        </p>

        <div class="suggestions">

            <button onclick="usarSugestao('Explique-me inteligência artificial de forma simples')">
                🤖
                <span>
                    <strong>Inteligência Artificial</strong>
                    Aprender conceitos de IA
                </span>
            </button>

            <button onclick="usarSugestao('Ajude-me a aprender programação')">
                💻
                <span>
                    <strong>Programação</strong>
                    Aprender a programar
                </span>
            </button>

            <button onclick="usarSugestao('Ajude-me com os meus estudos')">
                📚
                <span>
                    <strong>Estudos</strong>
                    Explicar matérias
                </span>
            </button>

            <button onclick="usarSugestao('Explique redes de computadores')">
                🌐
                <span>
                    <strong>Tecnologia</strong>
                    Redes e informática
                </span>
            </button>

        </div>
    ;

    chatBox.appendChild(novaTela);

    input.value = "";

    ajustarTextarea();

    input.focus();
}


// ===============================
// SIDEBAR MOBILE
// ===============================

function toggleSidebar() {

    const sidebar =
        document.getElementById("sidebar");

    sidebar.classList.toggle("open");
}


// ===============================
// HISTÓRICO SIMPLES
// ===============================

function adicionarHistorico(mensagem) {

    const history =
        document.getElementById("history");

    // Evitar mensagens enormes
    let titulo = mensagem;

    if (titulo.length > 35) {
        titulo = titulo.substring(0, 35) + "...";
    }

    const item =
        document.createElement("button");

    item.className = "history-item";

    item.textContent = "💬 " + titulo;

    item.onclick = function () {

        input.value = mensagem;

        ajustarTextarea();

        input.focus();
    };

    // Colocar no início
    history.prepend(item);

    // Limitar histórico visual
    while (history.children.length > 10) {

        history.removeChild(
            history.lastChild
        );
    }
}


// ===============================
// FECHAR SIDEBAR AO CLICAR FORA
// ===============================

document.addEventListener("click", function(event) {

    const sidebar =
        document.getElementById("sidebar");

    const menu =
        document.querySelector(".menu-button");

    if (
        window.innerWidth <= 800 &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(event.target) &&
        !menu.contains(event.target)
    ) {

        sidebar.classList.remove("open");
    }
});


// ===============================
// INICIAR
// ===============================

input.focus();

