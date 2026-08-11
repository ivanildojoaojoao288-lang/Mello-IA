// =====================================================
// MELLO IA — SCRIPT ULTRA PRO MAX
// CHAT + IMAGEM + MICROFONE + VOZ + HISTÓRICO
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

let recognition = null;
let ouvindo = false;

let falarResposta = true;

let voices = [];


// =====================================================
// VERIFICAR ELEMENTOS
// =====================================================

if (!input) {
    console.error("Campo user-input não encontrado.");
}


// =====================================================
// VOZES DO NAVEGADOR
// =====================================================

function carregarVozes() {

    if (!("speechSynthesis" in window)) {
        return;
    }

    voices = window.speechSynthesis.getVoices();

}

if ("speechSynthesis" in window) {

    carregarVozes();

    window.speechSynthesis.onvoiceschanged =
        carregarVozes;
}


// =====================================================
// ESCOLHER VOZ PORTUGUESA
// =====================================================

function obterVozPortugues() {

    if (!voices.length) {
        return null;
    }

    const preferidas = [
        "Google português",
        "Google Português",
        "Microsoft Francisca",
        "Microsoft Maria",
        "Microsoft Helena",
        "Microsoft António",
        "Portuguese",
        "Português"
    ];

    for (const nome of preferidas) {

        const encontrada =
            voices.find(
                voz =>
                    voz.name
                        .toLowerCase()
                        .includes(
                            nome.toLowerCase()
                        )
            );

        if (encontrada) {
            return encontrada;
        }
    }


    return (
        voices.find(
            voz =>
                voz.lang &&
                voz.lang
                    .toLowerCase()
                    .startsWith("pt")
        )
        || null
    );
}


// =====================================================
// FALAR RESPOSTA
// =====================================================

function falar(texto) {

    if (!falarResposta) {
        return;
    }

    if (!("speechSynthesis" in window)) {
        return;
    }

    if (!texto) {
        return;
    }


    window.speechSynthesis.cancel();


    // Remover Markdown básico
    const textoLimpo =
        texto
            .replace(/```[\s\S]*?```/g, " ")
            .replace(/[*_#>`]/g, "")
            .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
            .replace(/\s+/g, " ")
            .trim();


    if (!textoLimpo) {
        return;
    }


    const utterance =
        new SpeechSynthesisUtterance(
            textoLimpo
        );


    const voz =
        obterVozPortugues();


    if (voz) {
        utterance.voice = voz;
    }


    utterance.lang = "pt-PT";

    utterance.rate = 0.95;

    utterance.pitch = 1.02;

    utterance.volume = 1;


    utterance.onstart = function () {

        document.body.classList.add(
            "mello-speaking"
        );

    };


    utterance.onend = function () {

        document.body.classList.remove(
            "mello-speaking"
        );

    };


    utterance.onerror = function () {

        document.body.classList.remove(
            "mello-speaking"
        );

    };


    window.speechSynthesis.speak(
        utterance
    );

}


// =====================================================
// PARAR VOZ
// =====================================================

function pararVoz() {

    if (
        "speechSynthesis"
        in window
    ) {

        window.speechSynthesis.cancel();

    }

}


// =====================================================
// MICROFONE
// =====================================================

function iniciarMicrofone() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        alert(
            "O reconhecimento de voz não é suportado neste navegador. Tenta usar Google Chrome ou Microsoft Edge."
        );

        return;

    }


    if (ouvindo) {

        pararMicrofone();

        return;

    }


    recognition =
        new SpeechRecognition();


    recognition.lang = "pt-PT";

    recognition.continuous = false;

    recognition.interimResults = true;

    recognition.maxAlternatives = 1;


    recognition.onstart =
        function () {

            ouvindo = true;

            atualizarMicrofone(true);

        };


    recognition.onresult =
        function (event) {

            let resultadoFinal = "";

            let resultadoIntermedio = "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const transcript =
                    event.results[i][0]
                        .transcript;


                if (
                    event.results[i].isFinal
                ) {

                    resultadoFinal +=
                        transcript;

                } else {

                    resultadoIntermedio +=
                        transcript;

                }

            }


            if (resultadoFinal) {

                input.value =
                    (
                        input.value +
                        " " +
                        resultadoFinal
                    ).trim();

            } else {

                input.value =
                    (
                        input.value +
                        " " +
                        resultadoIntermedio
                    ).trim();

            }


            ajustarTextarea();

        };


    recognition.onerror =
        function (event) {

            console.error(
                "Erro no microfone:",
                event.error
            );


            if (
                event.error ===
                "not-allowed"
            ) {

                alert(
                    "Permissão do microfone recusada. Permite o acesso ao microfone no navegador."
                );

            }

        };


    recognition.onend =
        function () {

            ouvindo = false;

            atualizarMicrofone(false);

            ajustarTextarea();

            input.focus();

        };


    try {

        recognition.start();

    } catch (erro) {

        console.error(
            "Não foi possível iniciar o microfone:",
            erro
        );

    }

}


// =====================================================
// PARAR MICROFONE
// =====================================================

function pararMicrofone() {

    if (recognition) {

        try {

            recognition.stop();

        } catch (erro) {

            console.log(
                "Microfone já estava parado."
            );

        }

    }


    ouvindo = false;

    atualizarMicrofone(false);

}


// =====================================================
// ATUALIZAR BOTÃO DO MICROFONE
// =====================================================

function atualizarMicrofone(ativo) {

    const mic =
        document.querySelector(
            ".mic-button"
        );


    if (!mic) {
        return;
    }


    if (ativo) {

        mic.classList.add(
            "recording"
        );

        mic.setAttribute(
            "title",
            "Parar gravação"
        );

        mic.setAttribute(
            "aria-label",
            "Parar gravação"
        );


        mic.innerHTML = "■";

    } else {

        mic.classList.remove(
            "recording"
        );

        mic.setAttribute(
            "title",
            "Falar com a Mello IA"
        );

        mic.setAttribute(
            "aria-label",
            "Falar com a Mello IA"
        );


        mic.innerHTML = "🎙";

    }

}


// =====================================================
// CRIAR MICROFONE AUTOMATICAMENTE
// =====================================================

function criarMicrofone() {

    if (!document.querySelector(".mic-button")) {

        const mic =
            document.createElement(
                "button"
            );


        mic.type = "button";

        mic.className =
            "mic-button";


        mic.innerHTML = "🎙";


        mic.title =
            "Falar com a Mello IA";


        mic.setAttribute(
            "aria-label",
            "Falar com a Mello IA"
        );


        mic.onclick =
            iniciarMicrofone;


        const inputBox =
            document.querySelector(
                ".input-box"
            );


        if (
            inputBox &&
            sendButton
        ) {

            inputBox.insertBefore(
                mic,
                sendButton
            );

        }

    }

}


// =====================================================
// IMAGEM
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

    imagemSelecionada = null;


    if (imageInput) {
        imageInput.value = "";
    }


    if (previewImage) {
        previewImage.src = "";
    }


    if (imageName) {
        imageName.textContent = "";
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

    const mensagem =
        input.value.trim();


    if (
        !mensagem &&
        !imagemSelecionada
    ) {

        return;

    }


    pararVoz();


    if (ouvindo) {
        pararMicrofone();
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


    input.value = "";

    removerImagem();

    ajustarTextarea();


    sendButton.disabled = true;


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


        const respostaIA =
            data.reply ||
            "Não consegui gerar uma resposta.";


        adicionarMensagem(
            "bot",
            respostaIA
        );


        adicionarHistorico(
            mensagemEnviar ||
            "📷 Imagem enviada"
        );


        // Falar automaticamente
        falar(
            respostaIA
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


    img.src = url;


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


    avatar.textContent = "M";


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

    if (!input) {
        return;
    }


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

    pararVoz();


    if (ouvindo) {
        pararMicrofone();
    }


    if (!chatBox) {
        return;
    }


    chatBox.innerHTML = "";


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

            <button
                onclick="usarSugestao(
                    'Explique-me inteligência artificial de forma simples'
                )"
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
                onclick="usarSugestao(
                    'Ajude-me a aprender programação'
                )"
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
                onclick="usarSugestao(
                    'Ajude-me com os meus estudos'
                )"
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
                onclick="usarSugestao(
                    'Explique redes de computadores'
                )"
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


    if (input) {

        input.value = "";

        ajustarTextarea();

        input.focus();

    }

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
        titulo.length > 35
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
// INICIALIZAÇÃO
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        criarMicrofone();

        if (input) {
            input.focus();
        }

    }
);
