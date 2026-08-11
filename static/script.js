/* =====================================================
   MELLO IA — SCRIPT PRINCIPAL
   Chat + Voz + Microfone + Imagem + Histórico
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
   VOZ
   ===================================================== */

function carregarVozes() {
    if ("speechSynthesis" in window) {
        vozes = window.speechSynthesis.getVoices();
    }
}

if ("speechSynthesis" in window) {
    carregarVozes();

    window.speechSynthesis.onvoiceschanged =
        carregarVozes;
}


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
            v.name &&
            v.name.toLowerCase().includes(
                nome.toLowerCase()
            )
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


function limparTextoParaVoz(texto) {

    return texto
        .replace(/```[\s\S]*?```/g, " ")
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
        .replace(/https?:\/\/\S+/g, "")
        .replace(/[*_#>`]/g, "")
        .replace(/\s+/g, " ")
        .trim();
}


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
            botao.classList.add("speaking");
            botao.innerHTML = "⏹";
            botao.title = "Parar voz";
        }
    };

    utteranceAtual.onend = function () {

        document.body.classList.remove(
            "mello-speaking"
        );

        if (botao) {
            botao.classList.remove("speaking");
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
            botao.classList.remove("speaking");
            botao.innerHTML = "🔊";
            botao.title = "Ouvir resposta";
        }

        utteranceAtual = null;
    };

    window.speechSynthesis.speak(
        utteranceAtual
    );
}


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
            "O reconhecimento de voz não está disponível. Use Google Chrome ou Microsoft Edge."
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
                    textoFinal += transcript;
                } else {
                    textoIntermedio += transcript;
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
                event.error === "not-allowed"
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
            "Erro ao iniciar microfone:",
            erro
        );
    }
}


function alternarMicrofone() {
    iniciarMicrofone();
}


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


function atualizarMicrofone(ativo) {

    const mic =
        document.querySelector(
            ".voice-button"
        );

    if (!mic) {
        return;
    }

    if (ativo) {

        mic.classList.add("recording");

        mic.innerHTML = "■";

        mic.title =
            "Parar gravação";

    } else {

        mic.classList.remove("recording");

        mic.innerHTML = "🎙️";

        mic.title =
            "Falar com a Mello IA";
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
                !arquivo.type.startsWith("image/")
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
        imagePreview.style.display = "none";
    }
}


/* =====================================================
   ENVIAR MENSAGEM
   ===================================================== */

async function enviarMensagem() {

    if (!input) {
        return;
    }

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

    const mensagemEnviar =
        mensagem;

    const imagemEnviar =
        imagemSelecionada;

    const welcome =
        document.getElementById(
            "welcome"
        );

    if (welcome) {
        welcome.style.display = "none";
    }

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

    if (sendButton) {
        sendButton.disabled = true;
    }

    const loading =
        adicionarLoading();

    try {

        /*
         * O app.py atual recebe JSON.
         * A imagem é mostrada no frontend,
         * mas não é enviada ao modelo neste momento.
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

        if (loading) {
            loading.remove();
        }

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
                "Ocorreu um erro no servidor."
            );

            return;
        }

        const respostaIA =
            data.reply ||
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

    } catch (erro) {

        console.error(
            "Erro de conexão:",
            erro
        );

        if (loading) {
            loading.remove();
        }

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


/* =====================================================
   MENSAGEM
   ===================================================== */

function adicionarMensagem(
    tipo,
    texto
) {

    if (!chatBox) {
        return;
    }

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

        const voiceButton =
            document.createElement(
                "button"
            );

        voiceButton.className =
            "message-voice-button";

        voiceButton.innerHTML = "🔊";

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

    message.appendChild(avatar);

    message.appendChild(content);

    chatBox.appendChild(message);

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

    if (!chatBox) {
        return;
    }

    const message =
        document.createElement(
            "div"
        );

    message.className =
        `message ${tipo}`;

    const avatar =
        document.createElement(
           
