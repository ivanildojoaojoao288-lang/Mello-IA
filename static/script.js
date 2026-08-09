// =====================================================
// MELLO IA — SCRIPT PRINCIPAL
// Texto + Imagem + Histórico
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


// =====================================================
// VERIFICAR ELEMENTOS
// =====================================================

if (!input) {
    console.error("Mello IA: #user-input não encontrado.");
}

if (!chatBox) {
    console.error("Mello IA: #chat-box não encontrado.");
}

if (!sendButton) {
    console.error("Mello IA: #send-button não encontrado.");
}


// =====================================================
// SELECIONAR IMAGEM
// =====================================================

if (imageInput) {

    imageInput.addEventListener("change", function () {

        const arquivo = this.files[0];

        if (!arquivo) {
            return;
        }


        // Verificar tipo
        if (!arquivo.type.startsWith("image/")) {

            alert("Selecione uma imagem válida.");

            this.value = "";

            return;
        }


        // Limite de 10 MB
        if (arquivo.size > 10 * 1024 * 1024) {

            alert(
                "A imagem é demasiado grande. " +
                "O limite máximo é 10 MB."
            );

            this.value = "";

            return;
        }


        imagemSelecionada = arquivo;


        // Criar preview
        const leitor = new FileReader();


        leitor.onload = function (event) {

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


        leitor.onerror = function () {

            alert("Não foi possível carregar a imagem.");

            removerImagem();

        };


        leitor.readAsDataURL(arquivo);

    });

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
        imagePreview.style.display = "none";
    }

}


// =====================================================
// ENVIAR MENSAGEM
// =====================================================

async function enviarMensagem() {

    const mensagem = input
        ? input.value.trim()
        : "";


    // Não enviar vazio
    if (!mensagem && !imagemSelecionada) {
        return;
    }


    // Esconder tela inicial
    const welcome =
        document.getElementById("welcome");


    if (welcome) {
        welcome.style.display = "none";
    }


    // Guardar imagem antes de limpar
    const imagemEnviar =
        imagemSelecionada;


    const mensagemEnviar =
        mensagem;


    // Mostrar mensagem do utilizador
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


    // Limpar input
    if (input) {
        input.value = "";
    }


    removerImagem();

    ajustarTextarea();


    // Desativar botão
    if (sendButton) {
        sendButton.disabled = true;
    }


    // Mostrar loading
    const loading =
        adicionarLoading();


    try {

        // =================================================
        // FORMDATA
        // =================================================

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


        // =================================================
        // ENVIAR PARA FLASK
        // =================================================

        const resposta =
            await fetch(
                "/chat",
                {
                    method: "POST",
                    body: formData
                }
            );


        // =================================================
        // LER RESPOSTA
        // =================================================

        let data = null;


        try {

            data =
                await resposta.json();

        } catch (erro) {

            console.error(
                "Resposta inválida:",
                erro
            );

            data = {
                reply:
                    "O servidor devolveu uma resposta inválida."
            };

        }


        // Remover loading
        if (loading) {
            loading.remove();
        }


        // =================================================
        // ERRO DO SERVIDOR
        // =================================================

        if (!resposta.ok) {

            adicionarMensagem(
                "bot",
                data.reply ||
                "Ocorreu um erro ao processar a mensagem."
            );

            return;
        }


        // =================================================
        // RESPOSTA DA MELLO IA
        // =================================================

        adicionarMensagem(
            "bot",
            data.reply ||
            "Não consegui gerar uma resposta."
        );


        // =================================================
        // HISTÓRICO
        // =================================================

        adicionarHistorico(
            mensagemEnviar ||
            "📷 Imagem enviada"
        );


    } catch (erro) {

        console.error(
            "Erro na comunicação:",
            erro
        );


        if (loading) {
            loading.remove();
        }


        adicionarMensagem(
            "bot",
            "Não consegui conectar ao servidor da Mello IA. " +
            "Verifique se o servidor está online."
        );


    } finally {

        if (sendButton) {
            sendButton.disabled = false;
        }


        if (input) {
            input.focus();
        }

    }

}


// =====================================================
// ADICIONAR MENSAGEM NORMAL
// =====================================================

function adicionarMensagem(tipo, texto) {

    const message =
       
