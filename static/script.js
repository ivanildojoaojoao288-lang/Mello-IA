// =====================================================
// MELLO IA — SCRIPT ULTRA PRO
// Chat + Imagem + Microfone + Voz + Histórico
// =====================================================

// =====================================================
// ELEMENTOS
// =====================================================

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");
const imageInput = document.getElementById("image-input");
const imagePreview = document.getElementById("image-preview");
const previewImage = document.getElementById("preview-image");
const imageName = document.getElementById("image-name");

// =====================================================
// ESTADO
// =====================================================

let imagemSelecionada = null;
let gravando = false;
let recognition = null;
let textoAntesDaGravacao = "";


// =====================================================
// CRIAR MICROFONE
// =====================================================

function criarMicrofone() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        return null;
    }

    const rec = new SpeechRecognition();

    rec.lang = "pt-MZ";
    rec.continuous = true;
    rec.interimResults = true;

    rec.onstart = function () {

        gravando = true;

        atualizarMicrofone(true);

    };

    rec.onresult = function (event) {

        let textoFinal = "";
        let textoIntermedio = "";

        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {

            const resultado =
                event.results[i];

            if (resultado.isFinal) {

                textoFinal +=
                    resultado[0].transcript;

            } else {

                textoIntermedio +=
                    resultado[0].transcript;

            }

        }

        input.value =
            textoAntesDaGravacao +
            textoFinal +
            textoIntermedio;

        ajustarTextarea();

    };

    rec.onerror = function (event) {

        console.error(
            "Erro no microfone:",
            event.error
        );

        if (
            event.error === "not-allowed"
        ) {

            alert(
                "Permite o acesso ao microfone para falar com a Mello IA."
            );

        }

        pararMicrofone();

    };

    rec.onend = function () {

        if (gravando) {

            try {

                rec.start();

            } catch (erro) {

                pararMicrofone();

            }

        }

    };

    return rec;
}


recognition =
    criarMicrofone();


// =====================================================
// CRIAR BOTÃO DE MICROFONE
// =====================================================

function criarBotaoMicrofone() {

    if (!input) {
        return;
    }

    const inputBox =
        input.closest(".input-box");

    if (!inputBox) {
        return;
    }

    let botao =
        document.getElementById(
            "microphone-button"
        );

    if (botao) {
        return;
    }

    botao =
        document.createElement("button");

    botao.type = "button";

    botao.id =
        "microphone-button";

    botao.className =
        "microphone-button";

    botao.title =
        "Falar com a Mello IA";

    botao.setAttribute(
        "aria-label",
        "Falar com a Mello IA"
    );

    botao.innerHTML = `
        <span class="mic-icon">🎙️</span>

        <span class="mic-waves">
            <i></i>
            <i></i>
            <i></i>
            <i></i>
            <i></i>
        </span>
    `;

    inputBox.insertBefore(
        botao,
        sendButton
    );

    botao.addEventListener(
        "click",
        alternarMicrofone
    );
}

criarBotaoMicrofone();


// =====================================================
// MICROFONE
// =====================================================

function alternarMicrofone() {

    if (!recognition) {

        alert(
            "O teu navegador não suporta reconhecimento de voz. Usa Google Chrome ou Microsoft Edge."
        );

        return;
    }

    if (gravando) {

        pararMicrofone();

    } else {

        iniciarMicrofone();

    }
}


// =====================================================
// INICIAR MICROFONE
// =====================================================

function iniciarMicrofone() {

    if (!recognition) {
        return;
    }

    textoAntesDaGravacao =
        input.value.trim();

    if (
        textoAntesDaGravacao
    ) {

        textoAntesDaGravacao +=
            " ";

    }

    gravando = true;

    atualizarMicrofone(true);

    try {

        recognition.start();

    } catch (erro) {

        console.log(
            "Microfone já iniciado."
        );

    }
}


// =====================================================
// PARAR MICROFONE
// =====================================================

function pararMicrofone() {

    gravando = false;

    atualizarMicrofone(false);

    if (!recognition) {
        return;
    }

    try {

        recognition.stop();

    } catch (erro) {

        console.log(
            "Microfone já parado."
        );

    }
}


// =====================================================
// ATUALIZAR INTERFACE DO MICROFONE
// =====================================================

function atualizarMicrofone(ativo) {

    const botao =
        document.getElementById(
            "microphone-button"
        );

    if (!botao) {
        return;
    }

    if (ativo) {

        botao.classList.add(
            "recording"
        );

        botao.title =
            "Parar gravação";

        botao.setAttribute(
            "aria-label",
            "Parar gravação"
        );

    } else {

        botao.classList.remove(
            "recording"
        );

        botao.title =
            "Falar com a Mello IA";

        botao.setAttribute(
            "aria-label",
            "Falar com a Mello IA"
        );

    }
}


// =====================================================
// SELECIONAR IMAGEM
// =====================================================

if (imageInput) {

    imageInput.addEventListener(
        "change",
        function () {

            const arquivo =
                this.files[0];

            if (!arquivo) {
                return;
            }

            if (
                !arquivo.type.startsWith(
                    "image/"
                )
            ) {

                alert(
                    "Selecione uma imagem válida."
                );

                this.value = "";

                return;
            }

            if (
                arquivo.size >
                10 * 1024 * 1024
            ) {

                alert(
                    "A imagem deve ter no máximo 10 MB."
                );

                this.value = "";

                return;
            }

            imagemSelecionada =
                arquivo;

            const leitor =
                new FileReader();

            leitor.onload =
                function (event) {

                    if (previewImage) {

                        previewImage.src =
                            event.target.result;

                    }

                    if (imageName) {

                        imageName.textContent =
                            arquivo.name;

                    }

                    if (imagePreview) {

                        imagePreview.style.display =
                            "flex";

                    }

                };

            leitor.readAsDataURL(
                arquivo
            );

        }
    );

}


// =====================================================
// REMOVER IMAGEM
// =====================================================

function removerImagem() {

    imagemSelecionada =
        null;

    if (imageInput) {

        imageInput.value =
            "";

    }

    if (previewImage) {

        previewImage.src =
            "";

    }

    if (imageName) {

        imageName.textContent =
            "";

    }

    if (imagePreview) {

        imagePreview.style.display =
            "none";

    }
}


// =====================================================
// ENVIAR MENSAGEM
// =====================================================

async function enviarMensagem() {

    // parar microfone
    if (gravando) {

        pararMicrofone();

    }

    const mensagem =
        input.value.trim();

    if (
        !mensagem &&
        !imagemSelecionada
    ) {

        return;

    }

    const welcome =
        document.getElementById(
            "welcome"
        );

    if (welcome) {

        welcome.style.display =
            "none";

    }

    const imagemEnviar =
        imagemSelecionada;

    const mensagemEnviar =
        mensagem;

    // mostrar mensagem do utilizador

    if (imagemEnviar) {

        adicionarMensagemImagem(
            "user",
            mensagemEnviar,
            imagemEnviar
        );

    } else {

        adicionarMensagem(
            "user",
            mensagemEnviar
        );

    }

    input.value =
        "";

    removerImagem();

    ajustarTextarea();

    sendButton.disabled =
        true;

    const loading =
        adicionarLoading();

    try {

        const formData =
            new FormData();

        if (mensagemEnviar) {

            formData.append(
                "message",
                mensagemEnviar
            );

        }

        if (imagemEnviar) {

            formData.append(
                "image",
                imagemEnviar
            );

        }

        const resposta =
            await fetch(
                "/chat",
                {
                    method: "POST",
                    body: formData
                }
            );

        let data;

        try {

            data =
                await resposta.json();

        } catch (erro) {

            data = {

                reply:
                    "O servidor devolveu uma resposta inválida."

            };

        }

        loading.remove();

        if (!resposta.ok) {

            adicionarMensagem(
                "bot",
                data.reply ||
                "Ocorreu um erro."
            );

            return;
        }

        adicionarMensagem(
            "bot",
            data.reply ||
            "Não consegui gerar uma resposta."
        );

        adicionarHistorico(
            mensagemEnviar ||
            "📷 Imagem enviada"
        );

    } catch (erro) {

        console.error(
            "Erro:",
            erro
        );

        loading.remove();

        adicionarMensagem(
            "bot",
            "Não consegui conectar ao servidor da Mello IA."
        );

    } finally {

        sendButton.disabled =
            false;

        input.focus();

    }
}


// =====================================================
// ADICIONAR MENSAGEM
// =====================================================

function adicionarMensagem(
    tipo,
    texto
) {

    const message =
        document.createElement(
            "div"
        );

    message.className =
        `message ${tipo}`;

    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "message-avatar";

    avatar.textContent =
        tipo === "bot"
            ? "M"
            : "👤";

    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";

    if (
        tipo === "bot" &&
        typeof marked !==
        "undefined"
    ) {

        const html =
            marked.parse(
                texto
            );

        if (
            typeof DOMPurify !==
            "undefined"
        ) {

            content.innerHTML =
                DOMPurify.sanitize(
                    html
                );

        } else {

            content.textContent =
                texto;

        }

    } else {

        content.textContent =
            texto;

    }

    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );

    chatBox.appendChild(
        message
    );

    scrollChat();

    return message;
}


// =====================================================
// MENSAGEM COM IMAGEM
// =====================================================

function adicionarMensagemImagem(
    tipo,
    texto,
    arquivo
) {

    const message =
        document.createElement(
            "div"
        );

    message.className =
        `message ${tipo}`;

    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "message-avatar";

    avatar.textContent =
        tipo === "bot"
            ? "M"
            : "👤";

    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";

    const img =
        document.createElement(
            "img"
        );

    img.className =
        "message-image";

    img.alt =
        "Imagem enviada";

    const url =
        URL.createObjectURL(
            arquivo
        );

    img.src =
        url;

    content.appendChild(
        img
    );

    if (texto) {

        const textoElemento =
            document.createElement(
                "div"
            );

        textoElemento.className =
            "image-message-text";

        textoElemento.textContent =
            texto;

        content.appendChild(
            textoElemento
        );

    }

    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );

    chatBox.appendChild(
        message
    );

    scrollChat();

    return message;
}


// =====================================================
// LOADING
// =====================================================

function adicionarLoading() {

    const message =
        document.createElement(
            "div"
        );

    message.className =
        "message bot";

    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "M";

    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";

    const loading =
        document.createElement(
            "div"
        );

    loading.className =
        "typing";

    loading.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    content.appendChild(
        loading
    );

    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );

    chatBox.appendChild(
        message
    );

    scrollChat();

    return message;
}


// =====================================================
// SCROLL
// =====================================================

function scrollChat() {

    if (!chatBox) {
        return;
    }

    chatBox.scrollTo({

        top:
            chatBox.scrollHeight,

        behavior:
            "smooth"

    });

}


// =====================================================
// ENTER
// =====================================================

function handleKey(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        enviarMensagem();

    }

}


// =====================================================
// TEXTAREA
// =====================================================

if (input) {

    input.addEventListener(
        "input",
        ajustarTextarea
    );

}


function ajustarTextarea() {

    if (!input) {
        return;
    }

    input.style.height =
        "auto";

    input.style.height =
        Math.min(
            input.scrollHeight,
            130
        ) + "px";

}


// =====================================================
// SUGESTÕES
// =====================================================

function usarSugestao(
    texto
) {

    input.value =
        texto;

    ajustarTextarea();

    input.focus();

    enviarMensagem();

}


// =====================================================
// NOVA CONVERSA
// =====================================================

function novaConversa() {

    chatBox.innerHTML =
        "";

    const novaTela =
        document.createElement(
            "div"
        );

    novaTela.className =
        "welcome";

    novaTela.id =
        "welcome";

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
                    <strong>
                        Inteligência Artificial
                    </strong>
                    Aprender conceitos de IA
                </span>
            </button>

            <button onclick="usarSugestao('Ajude-me a aprender programação')">
                💻
                <span>
                    <strong>
                        Programação
                    </strong>
                    Aprender a programar
                </span>
            </button>

            <button onclick="usarSugestao('Ajude-me com os meus estudos')">
                📚
                <span>
                    <strong>
                        Estudos
                    </strong>
                    Explicar matérias
                </span>
            </button>

            <button onclick="usarSugestao('Explique redes de computadores')">
                🌐
                <span>
                    <strong>
                        Tecnologia
                    </strong>
                    Redes e informática
                </span>
            </button>

        </div>
    `;

    chatBox.appendChild(
        novaTela
    );

    removerImagem();

    input.value =
        "";

    ajustarTextarea();

    input.focus();

}


// =====================================================
// SIDEBAR
// =====================================================

function toggleSidebar() {

    const sidebar =
        document.getElementById(
            "sidebar"
        );

    if (sidebar) {

        sidebar.classList.toggle(
            "open"
        );

    }

}


// =====================================================
// HISTÓRICO
// =====================================================

function adicionarHistorico(
    mensagem
) {

    const history =
        document.getElementById(
            "history"
        );

    if (!history) {
        return;
    }

    let titulo =
        mensagem;

    if (
        titulo.length >
        35
    ) {

        titulo =
            titulo.substring(
                0,
                35
            ) + "...";

    }

    const item =
        document.createElement(
            "button"
        );

    item.className =
        "history-item";

    item.textContent =
        "💬 " + titulo;

    item.onclick =
        function () {

            input.value =
                mensagem;

            ajustarTextarea();

            input.focus();

        };

    history.prepend(
        item
    );

    while (
        history.children.length >
        10
    ) {

        history.removeChild(
            history.lastChild
        );

    }

}


// =====================================================
// FECHAR SIDEBAR
// =====================================================

document.addEventListener(
    "click",
    function (event) {

        const sidebar =
            document.getElementById(
                "sidebar"
            );

        const menu =
            document.querySelector(
                ".menu-button"
            );

        if (

            window.innerWidth <= 800 &&

            sidebar &&

            sidebar.classList.contains(
                "open"
            ) &&

            !sidebar.contains(
                event.target
            ) &&

            menu &&

            !menu.contains(
                event.target
            )

        ) {

            sidebar.classList.remove(
                "open"
            );

        }

    }
);


// =====================================================
// INICIAR
// =====================================================

if (input) {

    input.focus();

}
