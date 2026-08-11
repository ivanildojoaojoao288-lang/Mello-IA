// =====================================================
// MELLO IA — SCRIPT PRINCIPAL
// CHAT + IMAGEM + VOZ
// =====================================================


// =====================================================
// ELEMENTOS
// =====================================================

const input =
    document.getElementById("user-input");

const chatBox =
    document.getElementById("chat-box");

const sendButton =
    document.getElementById("send-button");

const imageInput =
    document.getElementById("image-input");

const imagePreview =
    document.getElementById("image-preview");

const previewImage =
    document.getElementById("preview-image");

const imageName =
    document.getElementById("image-name");

const voiceButton =
    document.getElementById("voice-button");

const voiceStatus =
    document.getElementById("voice-status");


// =====================================================
// ESTADO
// =====================================================

let imagemSelecionada = null;

let reconhecimento = null;

let ouvindo = false;

let falando = false;


// =====================================================
// RECONHECIMENTO DE VOZ
// =====================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


if (SpeechRecognition) {

    reconhecimento =
        new SpeechRecognition();


    reconhecimento.lang =
        "pt-MZ";


    reconhecimento.continuous =
        false;


    reconhecimento.interimResults =
        true;


    reconhecimento.maxAlternatives =
        1;


    reconhecimento.onstart =
        function () {

            ouvindo =
                true;


            if (voiceButton) {

                voiceButton.classList.add(
                    "recording"
                );

                voiceButton.textContent =
                    "🔴";

            }


            mostrarStatusVoz(
                "A ouvir... fala com a Mello IA 🎙️"
            );

        };


    reconhecimento.onresult =
        function (event) {

            let textoFinal =
                "";

            let textoParcial =
                "";


            for (
                let i = event.resultIndex;
                i < event.results.length;
                i++
            ) {

                const resultado =
                    event.results[i];


                const texto =
                    resultado[0].transcript;


                if (
                    resultado.isFinal
                ) {

                    textoFinal +=
                        texto;

                } else {

                    textoParcial +=
                        texto;

                }

            }


            if (textoFinal) {

                input.value =
                    textoFinal.trim();

            } else if (textoParcial) {

                input.value =
                    textoParcial.trim();

            }


            ajustarTextarea();

        };


    reconhecimento.onerror =
        function (event) {

            console.error(
                "Erro de reconhecimento:",
                event.error
            );


            if (
                event.error ===
                "not-allowed"
            ) {

                mostrarStatusVoz(
                    "Permissão do microfone foi recusada."
                );

            } else if (
                event.error ===
                "no-speech"
            ) {

                mostrarStatusVoz(
                    "Não ouvi nenhuma fala."
                );

            } else {

                mostrarStatusVoz(
                    "Não foi possível usar o microfone."
                );

            }

        };


    reconhecimento.onend =
        function () {

            ouvindo =
                false;


            if (voiceButton) {

                voiceButton.classList.remove(
                    "recording"
                );

                voiceButton.textContent =
                    "🎙️";

            }


            setTimeout(
                function () {

                    limparStatusVoz();

                },
                2000
            );

        };

} else {

    console.warn(
        "Reconhecimento de voz não suportado."
    );

}


// =====================================================
// MICROFONE
// =====================================================

function alternarMicrofone() {

    if (!reconhecimento) {

        alert(
            "O teu navegador não suporta reconhecimento de voz. Tenta usar Google Chrome."
        );

        return;

    }


    if (ouvindo) {

        reconhecimento.stop();

        return;

    }


    try {

        reconhecimento.start();

    } catch (erro) {

        console.error(
            erro
        );

    }

}


// =====================================================
// STATUS DA VOZ
// =====================================================

function mostrarStatusVoz(
    mensagem
) {

    if (!voiceStatus) {
        return;
    }


    voiceStatus.textContent =
        mensagem;


    voiceStatus.classList.add(
        "active"
    );

}


function limparStatusVoz() {

    if (!voiceStatus) {
        return;
    }


    voiceStatus.textContent =
        "";


    voiceStatus.classList.remove(
        "active"
    );

}


// =====================================================
// FALAR RESPOSTA DA MELLO
// =====================================================

function falarTexto(
    texto,
    botao
) {

    if (
        !("speechSynthesis" in window)
    ) {

        alert(
            "O teu navegador não suporta leitura de voz."
        );

        return;

    }


    if (falando) {

        speechSynthesis.cancel();

        falando =
            false;


        if (botao) {

            botao.textContent =
                "🔊 Ouvir";

        }

        return;

    }


    const textoLimpo =
        limparTextoParaVoz(
            texto
        );


    if (!textoLimpo) {
        return;
    }


    speechSynthesis.cancel();


    const utterance =
        new SpeechSynthesisUtterance(
            textoLimpo
        );


    utterance.lang =
        "pt-MZ";


    utterance.rate =
        0.95;


    utterance.pitch =
        1;


    utterance.volume =
        1;


    const vozes =
        speechSynthesis.getVoices();


    const vozPortugues =
        vozes.find(
            function (voz) {

                return (
                    voz.lang &&
                    voz.lang
                        .toLowerCase()
                        .startsWith("pt")
                );

            }
        );


    if (vozPortugues) {

        utterance.voice =
            vozPortugues;

    }


    utterance.onstart =
        function () {

            falando =
                true;


            if (botao) {

                botao.textContent =
                    "⏹️ Parar";

            }

        };


    utterance.onend =
        function () {

            falando =
                false;


            if (botao) {

                botao.textContent =
                    "🔊 Ouvir";

            }

        };


    utterance.onerror =
        function () {

            falando =
                false;


            if (botao) {

                botao.textContent =
                    "🔊 Ouvir";

            }

        };


    speechSynthesis.speak(
        utterance
    );

}


// =====================================================
// LIMPAR MARKDOWN PARA VOZ
// =====================================================

function limparTextoParaVoz(
    texto
) {

    if (!texto) {
        return "";
    }


    let resultado =
        texto;


    resultado =
        resultado.replace(
            /https?:\/\/\S+/gi,
            ""
        );


    resultado =
        resultado.replace(
            /\[([^\]]+)\]\([^)]+\)/g,
            "$1"
        );


    resultado =
        resultado.replace(
            /^#{1,6}\s*/gm,
            ""
        );


    resultado =
        resultado.replace(
            /\*\*(.*?)\*\*/g,
            "$1"
        );


    resultado =
        resultado.replace(
            /\*(.*?)\*/g,
            "$1"
        );


    resultado =
        resultado.replace(
            /```[\s\S]*?```/g,
            " bloco de código "
        );


    resultado =
        resultado.replace(
            /`([^`]+)`/g,
            "$1"
        );


    resultado =
        resultado.replace(
            /[\u{1F300}-\u{1FAFF}]/gu,
            ""
        );


    resultado =
        resultado.replace(
            /\n{2,}/g,
            ". "
        );


    resultado =
        resultado.replace(
            /\s{2,}/g,
            " "
        );


    return resultado.trim();

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


            if (!arquivo.type.startsWith("image/")) {

                alert(
                    "Selecione uma imagem válida."
                );

                this.value =
                    "";

                return;

            }


            if (
                arquivo.size >
                10 * 1024 * 1024
            ) {

                alert(
                    "A imagem deve ter no máximo 10 MB."
                );

                this.value =
                    "";

                return;

            }


            imagemSelecionada =
                arquivo;


            const leitor =
                new FileReader();


            leitor.onload =
                function (event) {

                    if (previewImage) {
                        previewImage.src = event.target.result;
                    }

                    if (imageName) {
                        imageName.textContent = arquivo.name;
                    }

                    if (imagePreview) {
                        imagePreview.style.display = "flex";
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

    if (!input) return;

    const mensagem =
        input.value.trim();


    if (
        !mensagem &&
        !imagemSelecionada
    ) {

        return;

    }


    if (
        "speechSynthesis" in window
    ) {

        speechSynthesis.cancel();

        falando =
            false;

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


    input.value =
        "";


    removerImagem();


    ajustarTextarea();


    if (sendButton) {
        sendButton.disabled = true;
    }


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
                    method:
                        "POST",

                    body:
                        formData
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

        if (sendButton) {
            sendButton.disabled = false;
        }

        input.focus();

    }

}


// =====================================================
// MENSAGEM NORMAL
// =====================================================

function adicionarMensagem(
    tipo,
    texto
) {

    if (!chatBox) return;

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
        typeof marked !== "undefined"
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

        const voiceReplyButton =
            document.createElement(
                "button"
            );


        voiceReplyButton.type =
            "button";


        voiceReplyButton.className =
            "reply-voice-button";


        voiceReplyButton.textContent =
            "🔊 Ouvir";


        voiceReplyButton.title =
            "Ouvir resposta";


        voiceReplyButton.onclick =
            function () {

                falarTexto(
                    texto,
                    voiceReplyButton
                );

            };


        content.appendChild(
            voiceReplyButton
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
// MENSAGEM COM IMAGEM
// =====================================================

function adicionarMensagemImagem(
    tipo,
    texto,
    arquivo
) {

    if (!chatBox) return;

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

    if (!chatBox) return;

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

    if (!chatBox) return;

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

    input.addEventListener(
        "keydown",
        handleKey
    );

}


function ajustarTextarea() {

    if (!input) return;

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

    if (!input) return;

    input.value =
        texto;


    ajustarTextarea();

    input.focus();

    enviarMensagem();

        }
        
