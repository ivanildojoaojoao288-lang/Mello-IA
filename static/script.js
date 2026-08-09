// =====================================================
// MELLO IA — SCRIPT PRINCIPAL
// Chat + Imagens + Histórico + Interface
// =====================================================

const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendButton = document.getElementById("send-button");
const welcome = document.getElementById("welcome");

// =====================================================
// CRIAR INPUT DE IMAGEM
// =====================================================

let imageInput = document.getElementById("image-input");

if (!imageInput) {
    imageInput = document.createElement("input");

    imageInput.type = "file";
    imageInput.id = "image-input";
    imageInput.accept = "image/png,image/jpeg,image/webp,image/gif";
    imageInput.style.display = "none";

    document.body.appendChild(imageInput);
}

// Imagem atualmente selecionada
let imagemSelecionada = null;


// =====================================================
// BOTÃO + / ANEXAR
// =====================================================

const attachButton = document.querySelector(".attach-button");

if (attachButton) {

    attachButton.addEventListener("click", function () {

        imageInput.click();

    });

}


// =====================================================
// SELECIONAR IMAGEM
// =====================================================

imageInput.addEventListener("change", function () {

    const arquivo = this.files[0];

    if (!arquivo) return;

    // Limite de 10 MB
    if (arquivo.size > 10 * 1024 * 1024) {

        adicionarMensagem(
            "bot",
            "A imagem é muito grande. Escolha uma imagem com no máximo 10 MB."
        );

        this.value = "";
        return;
    }

    imagemSelecionada = arquivo;

    mostrarPreviewImagem(arquivo);

    input.focus();

});


// =====================================================
// PREVIEW DA IMAGEM
// =====================================================

function mostrarPreviewImagem(arquivo) {

    let preview = document.getElementById("image-preview");

    if (!preview) {

        preview = document.createElement("div");

        preview.id = "image-preview";

        preview.className = "image-preview";

        const inputWrapper =
            document.querySelector(".input-wrapper");

        if (inputWrapper) {
            inputWrapper.insertBefore(
                preview,
                inputWrapper.firstChild
            );
        } else {
            document.body.appendChild(preview);
        }
    }

    const url = URL.createObjectURL(arquivo);

    preview.innerHTML = "";

    const img = document.createElement("img");

    img.src = url;
    img.alt = "Imagem selecionada";

    const info = document.createElement("div");

    info.className = "image-preview-info";

    const nome = document.createElement("span");

    nome.textContent = arquivo.name;

    const remover = document.createElement("button");

    remover.type = "button";
    remover.textContent = "×";
    remover.title = "Remover imagem";

    remover.onclick = function () {

        imagemSelecionada = null;
        imageInput.value = "";

        preview.remove();
    };

    info.appendChild(nome);
    info.appendChild(remover);

    preview.appendChild(img);
    preview.appendChild(info);

}


// =====================================================
// ENVIAR MENSAGEM
// =====================================================

async function enviarMensagem() {

    const mensagem = input.value.trim();

    // Permitir enviar apenas imagem
    if (!mensagem && !imagemSelecionada) {
        return;
    }

    // Esconder tela inicial
    if (welcome) {
        welcome.style.display = "none";
    }

    // Guardar imagem atual
    const imagemAtual = imagemSelecionada;

    // Mostrar mensagem do utilizador
    adicionarMensagemUsuario(
        mensagem || "Analisa esta imagem.",
        imagemAtual
    );

    // Limpar campo
    input.value = "";

    ajustarTextarea();

    // Desativar botão
    sendButton.disabled = true;

    // Mostrar loading
    const loading = adicionarLoading();

    try {

        const formData = new FormData();

        formData.append(
            "message",
            mensagem || "Analisa esta imagem e explica o que encontraste."
        );

        if (imagemAtual) {

            formData.append(
                "image",
                imagemAtual
            );
        }


        const resposta = await fetch("/chat", {

            method: "POST",

            body: formData

        });


        let data;

        try {

            data = await resposta.json();

        } catch (erro) {

            data = {
                reply: "O servidor devolveu uma resposta inválida."
            };

        }


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


        // Resposta da IA
        adicionarMensagem(
            "bot",
            data.reply ||
            "Não consegui gerar uma resposta."
        );


        // Histórico
        adicionarHistorico(
            mensagem ||
            "Análise de imagem"
        );


    } catch (erro) {

        console.error("Erro:", erro);

        loading.remove();

        adicionarMensagem(
            "bot",
            "Não consegui conectar ao servidor da Mello IA. Verifique se o servidor está online."
        );


    } finally {

        sendButton.disabled = false;

        // Limpar imagem
        imagemSelecionada = null;

        imageInput.value = "";

        const preview =
            document.getElementById("image-preview");

        if (preview
