// ===============================
// MELLO IA - SCRIPT PRINCIPAL
// ===============================

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");
let welcome = document.getElementById("welcome");

// ===============================
// IMAGEM
// ===============================

let imagemSelecionada = null;

const imageInput = document.getElementById("image-input");
const attachButton = document.getElementById("attach-button");

// Abrir seletor de imagem
if (attachButton && imageInput) {
    attachButton.addEventListener("click", function () {
        imageInput.click();
    });
}

// Quando escolher uma imagem
if (imageInput) {

    imageInput.addEventListener("change", function () {

        const arquivo = this.files[0];

        if (!arquivo) return;

        // Aceitar apenas imagens
        if (!arquivo.type.startsWith("image/")) {

            alert("Por favor selecione uma imagem válida.");

            this.value = "";

            return;
        }

        // Limitar tamanho para evitar problemas
        if (arquivo.size > 10 * 1024 * 1024) {

            alert("A imagem deve ter no máximo 10 MB.");

            this.value = "";

            return;
        }

        imagemSelecionada = arquivo;

        mostrarPreviewImagem(arquivo);
    });
}


// ===============================
// PREVIEW DA IMAGEM
// ===============================

function mostrarPreviewImagem(arquivo) {

    const reader = new FileReader();

    reader.onload = function (event) {

        // Remover preview anterior
        const antigo =
            document.getElementById("image-preview");

        if (antigo) {
            antigo.remove();
        }

        const preview =
            document.createElement("div");

        preview.id = "image-preview";

        preview.style.cssText = `
            max-width: 850px;
            margin: 0 auto 10px;
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
        ;

        const img =
            document.createElement("img");

        img.src = event.target.result;

        img.style.cssText = `
            width: 70px;
            height: 70px;
            object-fit: cover;
            border-radius: 10px;
        ;

        const texto =
            document.createElement("span");

        texto.textContent =
            "Imagem pronta para enviar";

        texto.style.cssText = `
            flex: 1;
            font-size: 13px;
            color: #475569;
        ;

        const remover =
            document.createElement("button");

        remover.textContent = "×";

        remover.title = "Remover imagem";

        remover.style.cssText = `
            width: 32px;
            height: 32px;
            border: none;
            border-radius: 50%;
            background: #f1f5f9;
            color: #475569;
            font-size: 20px;
            cursor: pointer;
        ;

        remover.onclick = function () {

            imagemSelecionada = null;

            if (imageInput) {
                imageInput.value = "";
            }

            preview.remove();
        };

        preview.appendChild(img);
        preview.appendChild(texto);
        preview.appendChild(remover);

        const wrapper =
            document.querySelector(".input-wrapper");

        wrapper.insertBefore(preview, wrapper.firstChild);
    };

    reader.readAsDataURL(arquivo);
}


// ===============================
// ENVIAR MENSAGEM
// ===============================

async function enviarMensagem() {

    const mensagem = input.value.trim();

    // Não permitir envio vazio
    // se também não houver imagem
    if (!mensagem && !imagemSelecionada) {
        return;
    }

    // Esconder tela inicial
    if (welcome) {
        welcome.style.display = "none";
    }

    // Guardar imagem atual
    const arquivoAtual = imagemSelecionada;

    // Converter imagem para Base64
    let imagemBase64 = null;

    if (arquivoAtual) {

        try {

            imagemBase64 =
                await converterImagemParaBase64(arquivoAtual);

        } catch (erro) {

            console.error(
                "Erro ao ler imagem:",
                erro
            );

            adicionarMensagem(
                "bot",
                "Não consegui ler a imagem. Tenta novamente."
            );

            return;
        }
    }

    // Mostrar mensagem do utilizador
    adicionarMensagemUsuario(
        mensagem,
        imagemBase64
    );

    // Guardar texto antes de limpar
    const mensagemHistorico =
        mensagem || "Imagem enviada";

    // Limpar campo
    input.value = "";

    ajustarTextarea();

    // Remover preview
    const preview =
        document.getElementById("image-preview");

    if (preview) {
        preview.remove();
    }

    // Limpar seleção
    imagemSelecionada = null;

    if (imageInput) {
        imageInput.value = "";
    }

    // Desativar botão
    sendButton.disabled = true;

    // Mostrar indicador
    const loading =
        adicionarLoading();

    try {

        const resposta =
            await fetch("/chat", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    message: mensagem,

                    image: imagemBase64
                })
            });

        const data =
            await resposta.json();

        // Remover loading
        loading.remove();

        if (!resposta.ok) {

            adicionarMensagem(
                "bot",
                data.reply ||
                "Ocorreu um erro ao processar a mensagem."
            );

            return;
        }

        // Mostrar resposta
        adicionarMensagem(
            "bot",
            data.reply ||
            "Não consegui gerar uma resposta."
        );

        // Histórico
        adicionarHistorico(
            mensagemHistorico
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


// ===============================
// CONVERTER IMAGEM
// ===============================

function converterImagemParaBase64(arquivo) {

    return new Promise(
        function (resolve, reject) {

            const reader =
                new FileReader();

            reader.onload =
                function () {
                    resolve(reader.result);
                };

            reader.onerror =
                function () {
                    reject(
                        new Error(
                            "Falha ao ler imagem."
                        )
                    );
                };

            reader.readAsDataURL(arquivo);
        }
    );
}


// ===============================
// MENSAGEM DO UTILIZADOR
// ===============================

function adicionarMensagemUsuario(
    texto,
    imagem
) {

    const message =
        document.createElement("div");

    message.className =
        "message user";

    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "👤";

    const content =
        document.createElement("div");

    content.className =
        "message-content";

    // Mostrar imagem
    if (imagem) {

        const img =
            document.createElement("img");

        img.src = imagem;

        img.style.cssText = `
            display: block;
            max-width: 280px;
            max-height: 300px;
            width: auto;
            height: auto;
            object-fit: contain;
            border-radius: 12px;
            margin-bottom: ${texto ? "10px" : "0"};
        ;

        content.appendChild(img);
    }

    // Mostrar texto
    if (texto) {

        const textoElement =
            document.createElement("div");

        textoElement.textContent =
            texto;

        content.appendChild(
            textoElement
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

    chatBox.scrollTo({

        top:
            chatBox.scrollHeight,

        behavior:
            "smooth"
    });

    return message;
}


// ===============================
// ADICIONAR MENSAGEM DA IA
// ===============================

function adicionarMensagem(
    tipo,
    texto
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

    // Por segurança, não inserir HTML
    // vindo diretamente da API
    content.textContent =
        texto;

    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );

    chatBox.appendChild(
        message
    );

    chatBox.scrollTo({

        top:
            chatBox.scrollHeight,

        behavior:
            "smooth"
    });

    return message;
}


// ===============================
// INDICADOR DE RESPOSTA
// ===============================

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
    ;

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

    chatBox.scrollTo({

        top:
            chatBox.scrollHeight,

        behavior:
            "smooth"
    });

    return message;
}


// ===============================
// ENTER PARA ENVIAR
// ===============================

function handleKey(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        enviarMensagem();
    }
}


// ===============================
// TEXTAREA AUTOMÁTICO
// ===============================

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


// ===============================
// SUGESTÕES
// ===============================

function usarSugestao(texto) {

    input.value =
        texto;

    ajustarTextarea();

    input.focus();

    enviarMensagem();
}


// ===============================
// NOVA CONVERSA
// ===============================

function novaConversa() {

    chatBox.innerHTML =
        "";

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

    chatBox.appendChild(
        novaTela
    );

    welcome =
        novaTela;

    input.value =
        "";

    ajustarTextarea();

    input.focus();
}


// ===============================
// SIDEBAR MOBILE
// ===============================

function toggleSidebar() {

    const sidebar =
        document.getElementById(
            "sidebar"
        );

    sidebar.classList.toggle(
        "open"
    );
}


// ===============================
// HISTÓRICO SIMPLES
// ===============================

function adicionarHistorico(
    mensagem
) {

    const history =
        document.getElementById(
            "history"
        );

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

    history.prepend(
        item
    );

    while (
        history.children.length > 10
    ) {

        history.removeChild(
            history.lastChild
        );
    }
}


// ===============================
// FECHAR SIDEBAR AO CLICAR FORA
// ===============================

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


// ===============================
// INICIAR
// ===============================

input.focus();
