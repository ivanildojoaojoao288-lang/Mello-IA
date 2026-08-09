// =====================================================
// MELLO IA — SCRIPT PRINCIPAL
// =====================================================


// ELEMENTOS

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");
const welcome = document.getElementById("welcome");

const imageInput = document.getElementById("image-input");
const imagePreview = document.getElementById("image-preview");
const previewImage = document.getElementById("preview-image");
const imageName = document.getElementById("image-name");


// IMAGEM SELECIONADA

let imagemSelecionada = null;


// =====================================================
// SELECIONAR IMAGEM
// =====================================================

imageInput.addEventListener("change", function () {

    const arquivo = this.files[0];

    if (!arquivo) {
        return;
    }

    if (!arquivo.type.startsWith("image/")) {

        alert("Selecione uma imagem válida.");

        this.value = "";

        return;
    }

    if (arquivo.size > 10 * 1024 * 1024) {

        alert("A imagem deve ter no máximo 10 MB.");

        this.value = "";

        return;
    }


    imagemSelecionada = arquivo;


    const leitor = new FileReader();


    leitor.onload = function (event) {

        previewImage.src = event.target.result;

        imageName.textContent = arquivo.name;

        imagePreview.style.display = "flex";

    };


    leitor.readAsDataURL(arquivo);

});


// =====================================================
// REMOVER IMAGEM
// =====================================================

function removerImagem() {

    imagemSelecionada = null;

    imageInput.value = "";

    previewImage.src = "";

    imageName.textContent = "";

    imagePreview.style.display = "none";

}


// =====================================================
// ENVIAR MENSAGEM
// =====================================================

async function enviarMensagem() {

    const mensagem = input.value.trim();


    // Não enviar vazio
    if (!mensagem && !imagemSelecionada) {
        return;
    }


    // Esconder welcome

    const telaWelcome =
        document.getElementById("welcome");

    if (telaWelcome) {
        telaWelcome.style.display = "none";
    }


    // Mostrar mensagem do utilizador

    if (imagemSelecionada) {

        adicionarMensagemImagem(
            "user",
            mensagem,
            imagemSelecionada
        );

    } else {

        adicionarMensagem(
            "user",
            mensagem
        );

    }


    // Guardar valores

    const mensagemEnviar = mensagem;
    const imagemEnviar = imagemSelecionada;


    // Limpar

    input.value = "";

    removerImagem();

    ajustarTextarea();


    // Desativar botão

    sendButton.disabled = true;


    // Loading

    const loading = adicionarLoading();


    try {

        const formData = new FormData();


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


        const resposta = await fetch(
            "/chat",
            {
                method: "POST",
                body: formData
            }
        );


        let data;


        try {

            data = await resposta.json();

        } catch (erro) {

            data = {
                reply:
                    "O servidor devolveu uma resposta inválida."
            };

        }


        // Remover loading

        loading.remove();


        // Erro

        if (!resposta.ok) {

            adicionarMensagem(
                "bot",
                data.reply ||
                "Ocorreu um erro ao processar a mensagem."
            );

            return;
        }


        // Resposta

        adicionarMensagem(
            "bot",
            data.reply ||
            "Não consegui gerar uma resposta."
        );


        // Histórico

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
            "Não consegui conectar ao servidor da Mello IA. Verifique se o servidor está online."
        );


    } finally {

        sendButton.disabled = false;

        input.focus();

    }

}


// =====================================================
// ADICIONAR MENSAGEM NORMAL
// =====================================================

function adicionarMensagem(tipo, texto) {

    const message =
        document.createElement("div");

    message.className =
        `message ${tipo}`;


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";


    avatar.textContent =
        tipo === "bot"
            ? "M"
            : "👤";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    // Segurança

    content.textContent =
        texto;


    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);


    scrollChat();


    return message;
}


// =====================================================
// ADICIONAR MENSAGEM COM IMAGEM
// =====================================================

function adicionarMensagemImagem(
    tipo,
    texto,
    arquivo
) {

    const message =
        document.createElement("div");

    message.className =
        `message ${tipo}`;


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";


    avatar.textContent =
        tipo === "bot"
            ? "M"
            : "👤";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const img =
        document.createElement("img");


    img.className =
        "message-image";


    img.alt =
        "Imagem enviada";


    const url =
        URL.createObjectURL(arquivo);


    img.src = url;


    content.appendChild(img);


    if (texto) {

        const textoElemento =
            document.createElement("div");

        textoElemento.className =
            "image-message-text";

        textoElemento.textContent =
            texto;

        content.appendChild(
            textoElemento
        );

    }


    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);


    scrollChat();


    return message;
}


// =====================================================
// LOADING
// =====================================================

function adicionarLoading() {

    const message =
        document.createElement("div");

    message.className =
        "message bot";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "M";


    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const loading =
        document.createElement("div");

    loading.className =
        "typing";


    loading.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;


    content.appendChild(loading);

    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);


    scrollChat();


    return message;
}


// =====================================================
// SCROLL
// =====================================================

function scrollChat() {

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
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

input.addEventListener(
    "input",
    ajustarTextarea
);


function ajustarTextarea() {

    input.style.height =
        "auto";


    input.style.height =
        Math.min(
            input.scrollHeight,
            130
        ) + "px";

}


// =====================================================
// SUGESTÃO
// =====================================================

function usarSugestao(texto) {

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

    chatBox.innerHTML = "";


    const novaTela =
        document.createElement("div");


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

            <button
                onclick="usarSugestao('Explique-me inteligência artificial de forma simples')"
            >
                🤖

                <span>
                    <strong>
                        Inteligência Artificial
                    </strong>

                    Aprender conceitos de IA
                </span>
            </button>


            <button
                onclick="usarSugestao('Ajude-me a aprender programação')"
            >
                💻

                <span>
                    <strong>
                        Programação
                    </strong>

                    Aprender a programar
                </span>
            </button>


            <button
                onclick="usarSugestao('Ajude-me com os meus estudos')"
            >
                📚

                <span>
                    <strong>
                        Estudos
                    </strong>

                    Explicar matérias
                </span>
            </button>


            <button
                onclick="usarSugestao('Explique redes de computadores')"
            >
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


    input.value = "";

    ajustarTextarea();

    input.focus();

}


// =====================================================
// SIDEBAR MOBILE
// =====================================================

function toggleSidebar() {

    const sidebar =
        document.getElementById(
            "sidebar"
        );


    sidebar.classList.toggle(
        "open"
    );

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


    if (titulo.length > 35) {

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


    history.prepend(item);


    while (
        history.children.length > 10
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
            sidebar.classList.contains("open") &&
            !sidebar.contains(event.target) &&
            menu &&
            !menu.contains(event.target)
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

input.focus();
