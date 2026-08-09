// ===============================
// MELLO IA - SCRIPT PRINCIPAL
// ===============================

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");
const welcome = document.getElementById("welcome");
const imageInput = document.getElementById("image-input");


// ===============================
// ENVIAR MENSAGEM
// ===============================

async function enviarMensagem() {

    const mensagem = input.value.trim();

    if (!mensagem) return;

    if (welcome) {
        welcome.style.display = "none";
    }

    adicionarMensagem("user", mensagem);

    input.value = "";

    ajustarTextarea();

    sendButton.disabled = true;

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

        loading.remove();

        if (!resposta.ok) {

            adicionarMensagem(
                "bot",
                data.reply || "Ocorreu um erro."
            );

            return;
        }

        adicionarMensagem(
            "bot",
            data.reply || "Não consegui gerar uma resposta."
        );

        adicionarHistorico(mensagem);

    } catch (erro) {

        console.error("Erro:", erro);

        loading.remove();

        adicionarMensagem(
            "bot",
            "Não consegui conectar ao servidor da Mello IA."
        );

    } finally {

        sendButton.disabled = false;

        input.focus();
    }
}


// ===============================
// ENVIAR IMAGEM
// ===============================

if (imageInput) {

    imageInput.addEventListener("change", async function () {

        const ficheiro = this.files[0];

        if (!ficheiro) return;

        if (!ficheiro.type.startsWith("image/")) {

            adicionarMensagem(
                "bot",
                "Por favor seleciona uma imagem válida."
            );

            return;
        }

        if (ficheiro.size > 8 * 1024 * 1024) {

            adicionarMensagem(
                "bot",
                "A imagem é muito grande. Escolhe uma imagem com menos de 8 MB."
            );

            return;
        }

        if (welcome) {
            welcome.style.display = "none";
        }

        const leitor = new FileReader();

        leitor.onload = async function () {

            const imagemBase64 = leitor.result;

            mostrarImagemUtilizador(imagemBase64);

            const loading = adicionarLoading();

            try {

                const resposta = await fetch("/vision", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        image: imagemBase64,

                        message:
                            "Analisa esta imagem cuidadosamente. Se houver texto, lê-o. Se houver uma conta matemática, resolve-a passo a passo. Se houver código, explica-o. Se houver um exercício, resolve-o. Explica tudo de forma clara e organizada."
                    })
                });

                const data = await resposta.json();

                loading.remove();

                if (!resposta.ok) {

                    adicionarMensagem(
                        "bot",
                        data.reply || "Não consegui analisar a imagem."
                    );

                    return;
                }

                adicionarMensagem(
                    "bot",
                    data.reply || "Imagem analisada."
                );

            } catch (erro) {

                console.error("Erro ao analisar imagem:", erro);

                loading.remove();

                adicionarMensagem(
                    "bot",
                    "Não consegui analisar esta imagem. Verifica a ligação ao servidor."
                );

            }

        };

        leitor.readAsDataURL(ficheiro);

        this.value = "";
    });
}


// ===============================
// MOSTRAR IMAGEM DO UTILIZADOR
// ===============================

function mostrarImagemUtilizador(src) {

    const message = document.createElement("div");

    message.className = "message user";

    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent = "👤";

    const content = document.createElement("div");

    content.className = "message-content image-message";

    const imagem = document.createElement("img");

    imagem.src = src;

    imagem.alt = "Imagem enviada";

    imagem.className = "uploaded-image";

    content.appendChild(imagem);

    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });
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

    content.textContent = texto;

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
// LOADING
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
    `;

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
// ENTER
// ===============================

function handleKey(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        enviarMensagem();
    }
}


// ===============================
// TEXTAREA
// ===============================

input.addEventListener(
    "input",
    ajustarTextarea
);

function ajustarTextarea() {

    input.style.height = "auto";

    input.style.height =
        Math.min(
            input.scrollHeight,
            130
        ) + "px";
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

    const novaTela =
        document.createElement("div");

    novaTela.className = "welcome";

    novaTela.id = "welcome";

    novaTela.innerHTML = `

        <div class="welcome-logo">
            M
        </div>

        <h1>
            Olá! Eu sou a
            <span>Mello IA</span>
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
    `;

    chatBox.appendChild(novaTela);

    input.value = "";

    ajustarTextarea();

    input.focus();
}


// ===============================
// SIDEBAR
// ===============================

function toggleSidebar() {

    const sidebar =
        document.getElementById("sidebar");

    sidebar.classList.toggle("open");
}


// ===============================
// HISTÓRICO
// ===============================

function adicionarHistorico(mensagem) {

    const history =
        document.getElementById("history");

    let titulo = mensagem;

    if (titulo.length > 35) {

        titulo =
            titulo.substring(0, 35) + "...";
    }

    const item =
        document.createElement("button");

    item.className =
        "history-item";

    item.textContent =
        "💬 " + titulo;

    item.onclick = function () {

        input.value = mensagem;

        ajustarTextarea();

        input.focus();
    };

    history.prepend(item);

    while (history.children.length > 10) {

        history.removeChild(
            history.lastChild
        );
    }
}


// ===============================
// FECHAR SIDEBAR
// ===============================

document.addEventListener(
    "click",
    function (event) {

        const sidebar =
            document.getElementById("sidebar");

        const menu =
            document.querySelector(
                ".menu-button"
            );

        if (
            window.innerWidth <= 800 &&
            sidebar.classList.contains("open") &&
            !sidebar.contains(event.target) &&
            !menu.contains(event.target)
        ) {

            sidebar.classList.remove("open");
        }
    }
);


// ===============================
// INICIAR
// ===============================

input.focus();
