/* =====================================================
MELLO IA — FRONTEND PRINCIPAL
Chat + Voz manual + Microfone + Imagem + Firebase
===================================================== */

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");

const imageInput = document.getElementById("image-input");
const imagePreview = document.getElementById("image-preview");
const previewImage = document.getElementById("preview-image");
const imageName = document.getElementById("image-name");

let imagemSelecionada = null;
let recognition = null;
let ouvindo = false;

let vozes = [];
let utteranceAtual = null;

/* =====================================================
VOZES
===================================================== */

function carregarVozes() {


if (!("speechSynthesis" in window)) {
    return;
}

vozes = window.speechSynthesis.getVoices();

}

if ("speechSynthesis" in window) {


carregarVozes();

window.speechSynthesis.onvoiceschanged =
    carregarVozes;

}

/* =====================================================
ENCONTRAR VOZ PORTUGUESA
===================================================== */

function obterVozPortugues() {


if (!vozes.length) {
    return null;
}

const preferidas = [
    "Microsoft Francisca",
    "Microsoft Maria",
    "Microsoft Helena",
    "Microsoft António",
    "Google português",
    "Google Português",
    "Portuguese",
    "Português"
];

for (const nome of preferidas) {

    const voz = vozes.find(v =>
        v.name
            .toLowerCase()
            .includes(nome.toLowerCase())
    );

    if (voz) {
        return voz;
    }
}

return (
    vozes.find(v =>
        v.lang &&
        v.lang.toLowerCase().startsWith("pt")
    ) || null
);


}

/* =====================================================
LIMPAR TEXTO PARA VOZ
===================================================== */

function limparTextoParaVoz(texto) {


return texto
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/[*_#>`]/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/https?:\/\/\S+/g, "")
    .replace(/\s+/g, " ")
    .trim();


}

/* =====================================================
FALAR — SOMENTE QUANDO CLICAR
===================================================== */

function falar(texto, botao = null) {

if (!("speechSynthesis" in window)) {

    alert(
        "O teu navegador não suporta reprodução de voz."
    );

    return;
}

if (!texto) {
    return;
}

if (window.speechSynthesis.speaking) {

    pararVoz();
    return;
}

const textoLimpo =
    limparTextoParaVoz(texto);

if (!textoLimpo) {
    return;
}

utteranceAtual =
    new SpeechSynthesisUtterance(
        textoLimpo
    );

const voz =
    obterVozPortugues();

if (voz) {
    utteranceAtual.voice = voz;
}

utteranceAtual.lang = "pt-PT";
utteranceAtual.rate = 0.95;
utteranceAtual.pitch = 1.02;
utteranceAtual.volume = 1;

utteranceAtual.onstart = function () {

    document.body.classList.add(
        "mello-speaking"
    );

    if (botao) {

        botao.classList.add(
            "speaking"
        );

        botao.innerHTML = "⏹";
        botao.title = "Parar voz";
    }
};

utteranceAtual.onend = function () {

    document.body.classList.remove(
        "mello-speaking"
    );

    if (botao) {

        botao.classList.remove(
            "speaking"
        );

        botao.innerHTML = "🔊";
        botao.title = "Ouvir resposta";
    }

    utteranceAtual = null;
};

utteranceAtual.onerror = function (erro) {

    console.error(
        "Erro de voz:",
        erro
    );

    document.body.classList.remove(
        "mello-speaking"
    );

    if (botao) {

        botao.classList.remove(
            "speaking"
        );

        botao.innerHTML = "🔊";
        botao.title = "Ouvir resposta";
    }

    utteranceAtual = null;
};

window.speechSynthesis.speak(
    utteranceAtual
);

}

/* =====================================================
PARAR VOZ
===================================================== */

function pararVoz() {


if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
}

document.body.classList.remove(
    "mello-speaking"
);

document
    .querySelectorAll(
        ".message-voice-button"
    )
    .forEach(botao => {

        botao.classList.remove(
            "speaking"
        );

        botao.innerHTML = "🔊";
        botao.title = "Ouvir resposta";
    });

utteranceAtual = null;


}

/* =====================================================
VOZ DA MENSAGEM
===================================================== */

function alternarVozMensagem(
texto,
botao
) {


if (
    "speechSynthesis" in window &&
    window.speechSynthesis.speaking
) {

    pararVoz();
    return;
}

falar(
    texto,
    botao
);


}

/* =====================================================
MICROFONE
===================================================== */

function iniciarMicrofone() {


const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

if (!SpeechRecognition) {

    alert(
        "O reconhecimento de voz não está disponível neste navegador. Use Google Chrome ou Microsoft Edge."
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

recognition.onstart = function () {

    ouvindo = true;

    atualizarMicrofone(true);
};

recognition.onresult =
    function (event) {

        let textoFinal = "";
        let textoIntermedio = "";

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

                textoFinal +=
                    transcript;

            } else {

                textoIntermedio +=
                    transcript;
            }
        }

        if (textoFinal) {

            input.value =
                (
                    input.value +
                    " " +
                    textoFinal
                ).trim();

        } else if (textoIntermedio) {

            input.value =
                (
                    input.value +
                    " " +
                    textoIntermedio
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
                "O acesso ao microfone foi recusado. Permite o microfone no navegador."
            );
        }
    };

recognition.onend =
    function () {

        ouvindo = false;

        atualizarMicrofone(false);

        if (input) {
            input.focus();
        }
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

/* =====================================================
PARAR MICROFONE
===================================================== */

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

/* =====================================================
ATUALIZAR MICROFONE
===================================================== */

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

    mic.innerHTML = "■";
    mic.title = "Parar gravação";

} else {

    mic.classList.remove(
        "recording"
    );

    mic.innerHTML = "🎙";
    mic.title = "Falar com a Mello IA";
}


}

/* =====================================================
CRIAR MICROFONE
===================================================== */

function criarMicrofone() {


if (
    document.querySelector(
        ".mic-button"
    )
) {
    return;
}

const inputBox =
    document.querySelector(
        ".input-box"
    );

if (!inputBox) {
    return;
}

const mic =
    document.createElement(
        "button"
    );

mic.type = "button";
mic.className = "mic-button";
mic.innerHTML = "🎙";
mic.title = "Falar com a Mello IA";

mic.addEventListener(
    "click",
    iniciarMicrofone
);

if (sendButton) {

    inputBox.insertBefore(
        mic,
        sendButton
    );

} else {

    inputBox.appendChild(
        mic
    );
}


}

/* =====================================================
IMAGEM
===================================================== */

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

/* =====================================================
REMOVER IMAGEM
===================================================== */

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

/* =====================================================
ENVIAR MENSAGEM
===================================================== */

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
    welcome.style.display = "none";
}

const mensagemEnviar =
    mensagem;

const imagemEnviar =
    imagemSelecionada;

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

    /*
     * O novo app.py espera JSON.
     *
     * Neste momento enviamos apenas texto.
     * A imagem continua sendo mostrada no frontend,
     * mas ainda não é enviada para análise pelo backend.
     */

    const resposta =
        await fetch(
            "/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message:
                        mensagemEnviar
                })
            }
        );

    let data;

    try {

        data =
            await resposta.json();

    } catch (erro) {

        data = {
            error:
                "O servidor devolveu uma resposta inválida."
        };
    }

    loading.remove();

    if (
        resposta.status === 401
    ) {

        window.location.href =
            "/login";

        return;
    }

    if (!resposta.ok) {

        adicionarMensagem(
            "bot",
            data.error ||
            "Ocorreu um erro."
        );

        return;
    }

    const respostaIA =
        data.response ||
        "Não consegui gerar uma resposta.";

    adicionarMensagem(
        "bot",
        respostaIA
    );

    adicionarHistorico(
        mensagemEnviar ||
        "📷 Imagem enviada"
    );

    /*
     * IMPORTANTE:
     *
     * A Mello NÃO fala automaticamente.
     *
     * O utilizador precisa clicar
     * no botão 🔊 da resposta.
     */

} catch (erro) {

    console.error(
        "Erro de conexão:",
        erro
    );

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

/* =====================================================
ADICIONAR MENSAGEM
===================================================== */

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

if (tipo === "bot") {

    const voiceButton =
        document.createElement(
            "button"
        );

    voiceButton.className =
        "message-voice-button";

    voiceButton.innerHTML =
        "🔊";

    voiceButton.title =
        "Ouvir resposta";

    voiceButton.setAttribute(
        "aria-label",
        "Ouvir resposta da Mello IA"
    );

    voiceButton.addEventListener(
        "click",
        function () {

            alternarVozMensagem(
                texto,
                voiceButton
            );
        }
    );

    content.appendChild(
        voiceButton
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

/* =====================================================
MENSAGEM COM IMAGEM
===================================================== */

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

img.src =
    URL.createObjectURL(
        arquivo
    );

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

/* =====================================================
LOADING
===================================================== */

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

scrollChat();

return message;

}

/* =====================================================
SCROLL
===================================================== */

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

/* =====================================================
ENTER
===================================================== */

function handleKey(event) {


if (
    event.key === "Enter" &&
    !event.shiftKey
) {

    event.preventDefault();

    enviarMensagem();
}


}

/* =====================================================
TEXTAREA
===================================================== */

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

/* =====================================================
SUGESTÕES
===================================================== */

function usarSugestao(texto) {


if (!input) {
    return;
}

input.value =
    texto;

ajustarTextarea();

input.focus();

enviarMensagem();
```

}

/* =====================================================
NOVA CONVERSA
===================================================== */

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

        <button onclick="usarSugestao(
            'Explique-me inteligência artificial de forma simples'
        )">

            🤖

            <span>

                <strong>
                    Inteligência Artificial
                </strong>

                Aprender conceitos de IA

            </span>

        </button>

        <button onclick="usarSugestao(
            'Ajude-me a aprender programação'
        )">

            💻

            <span>

                <strong>
                    Programação
                </strong>

                Aprender a programar

            </span>

        </button>

        <button onclick="usarSugestao(
            'Ajude-me com os meus estudos'
        )">

            📚

            <span>

                <strong>
                    Estudos
                </strong>

                Explicar matérias

            </span>

        </button>

        <button onclick="usarSugestao(
            'Explique redes de computadores'
        )">

            🌐

            <span>

                <strong>
                    Tecnologia
                </strong>

                Redes e informática

            </span>

        </button>

    </div>
;

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

/* =====================================================
SIDEBAR
===================================================== */

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

/* =====================================================
HISTÓRICO
===================================================== */

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
    "💬 " +
    titulo;

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

/* =====================================================
FECHAR SIDEBAR NO MOBILE
===================================================== */

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

/* =====================================================
ESC
===================================================== */

document.addEventListener(
"keydown",
function (event) {


    if (
        event.key === "Escape"
    ) {

        pararVoz();

        if (ouvindo) {
            pararMicrofone();
        }
    }
}


);

/* =====================================================
INICIALIZAÇÃO
===================================================== */

document.addEventListener(
"DOMContentLoaded",
function () {

```
    criarMicrofone();

    if (input) {
        input.focus();
    }
}

);
