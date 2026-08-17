/* =====================================================
   MELLO IA — LOGIN FIREBASE
   Google + Email/Password + Sessão Flask
   ===================================================== */

import {
    initializeApp
} from "https://www.gstatic.com/firebasejs/12.0.0/firebase-app.js";

import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    signInWithEmailAndPassword,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/12.0.0/firebase-auth.js";


/* =====================================================
   CONFIGURAÇÃO FIREBASE
   ===================================================== */

/*
 * IMPORTANTE:
 * Coloca aqui a configuração WEB do teu projeto Firebase.
 *
 * NÃO é o firebase-service-account.json.
 *
 * Esta configuração vem de:
 * Firebase Console
 * → Project settings
 * → Your apps
 * → Web app
 * → Firebase SDK setup
 */

const firebaseConfig = {

    apiKey: "COLOCA_AQUI",

    authDomain: "mello-ia.firebaseapp.com",

    projectId: "mello-ia",

    storageBucket: "mello-ia.firebasestorage.app",

    messagingSenderId: "COLOCA_AQUI",

    appId: "COLOCA_AQUI"

};


/* =====================================================
   FIREBASE
   ===================================================== */

const app =
    initializeApp(firebaseConfig);

const auth =
    getAuth(app);

const googleProvider =
    new GoogleAuthProvider();


/* =====================================================
   ELEMENTOS
   ===================================================== */

const googleButton =
    document.getElementById("google-login");

const loginForm =
    document.getElementById("login-form");

const emailInput =
    document.getElementById("email");

const passwordInput =
    document.getElementById("password");

const loginButton =
    document.getElementById("login-button");

const authMessage =
    document.getElementById("auth-message");


/* =====================================================
   MENSAGEM
   ===================================================== */

function mostrarMensagem(
    mensagem,
    erro = false
) {

    if (!authMessage) {
        return;
    }

    authMessage.textContent =
        mensagem;

    authMessage.style.color =
        erro
            ? "#dc2626"
            : "#0284c7";
}


/* =====================================================
   ESTADO DO BOTÃO
   ===================================================== */

function carregando(
    ativo
) {

    if (!loginButton) {
        return;
    }

    loginButton.disabled =
        ativo;

    loginButton.textContent =
        ativo
            ? "Entrando..."
            : "Entrar";

}


/* =====================================================
   ENVIAR TOKEN PARA FLASK
   ===================================================== */

async function criarSessaoFlask(
    user
) {

    if (!user) {
        throw new Error(
            "Utilizador Firebase inválido."
        );
    }

    const idToken =
        await user.getIdToken(
            true
        );


    const resposta =
        await fetch(
            "/auth/firebase",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        idToken:
                            idToken
                    })

            }
        );


    let dados;

    try {

        dados =
            await resposta.json();

    } catch {

        throw new Error(
            "O servidor devolveu uma resposta inválida."
        );

    }


    if (!resposta.ok) {

        throw new Error(
            dados.error ||
            "Não foi possível criar a sessão."
        );
    }


    if (!dados.success) {

        throw new Error(
            dados.error ||
            "Falha na autenticação."
        );
    }


    return dados;

}


/* =====================================================
   LOGIN GOOGLE
   ===================================================== */

if (googleButton) {

    googleButton.addEventListener(
        "click",
        async () => {

            try {

                googleButton.disabled =
                    true;

                googleButton.textContent =
                    "Entrando com Google...";


                mostrarMensagem(
                    "A autenticar com Google..."
                );


                const resultado =
                    await signInWithPopup(
                        auth,
                        googleProvider
                    );


                await criarSessaoFlask(
                    resultado.user
                );


                mostrarMensagem(
                    "Login efetuado. A abrir a Mello IA..."
                );


                window.location.href =
                    "/";


            } catch (erro) {

                console.error(
                    "Erro Google:",
                    erro
                );


                googleButton.disabled =
                    false;

                googleButton.innerHTML =
                    "<span>G</span> Continuar com Google";


                let mensagem =
                    "Não foi possível entrar com Google.";


                if (
                    erro.code ===
                    "auth/popup-closed-by-user"
                ) {

                    mensagem =
                        "A janela do Google foi fechada.";

                } else if (
                    erro.code ===
                    "auth/popup-blocked"
                ) {

                    mensagem =
                        "O navegador bloqueou a janela do Google.";

                } else if (
                    erro.code ===
                    "auth/unauthorized-domain"
                ) {

                    mensagem =
                        "Este domínio não está autorizado no Firebase.";

                } else if (
                    erro.code ===
                    "auth/operation-not-allowed"
                ) {

                    mensagem =
                        "O login com Google não está ativado no Firebase.";

                } else if (
                    erro.code ===
                    "auth/network-request-failed"
                ) {

                    mensagem =
                        "Erro de rede. Verifica a ligação.";

                } else {

                    mensagem =
                        erro.message ||
                        mensagem;
                }


                mostrarMensagem(
                    mensagem,
                    true
                );

            }

        }
    );

}


/* =====================================================
   LOGIN EMAIL + PASSWORD
   ===================================================== */

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();


            const email =
                emailInput
                    ?.value
                    .trim();

            const password =
                passwordInput
                    ?.value;


            if (!email || !password) {

                mostrarMensagem(
                    "Preenche o e-mail e a palavra-passe.",
                    true
                );

                return;
            }


            try {

                carregando(true);

                mostrarMensagem(
                    "A autenticar..."
                );


                const resultado =
                    await signInWithEmailAndPassword(
                        auth,
                        email,
                        password
                    );


                await criarSessaoFlask(
                    resultado.user
                );


                mostrarMensagem(
                    "Login efetuado. A abrir a Mello IA..."
                );


                window.location.href =
                    "/";


            } catch (erro) {

                console.error(
                    "Erro de login:",
                    erro
                );


                let mensagem =
                    "Não foi possível entrar.";


                switch (
                    erro.code
                ) {

                    case "auth/invalid-credential":
                        mensagem =
                            "E-mail ou palavra-passe incorretos.";
                        break;


                    case "auth/invalid-email":
                        mensagem =
                            "O e-mail não é válido.";
                        break;


                    case "auth/user-disabled":
                        mensagem =
                            "Esta conta foi desativada.";
                        break;


                    case "auth/user-not-found":
                        mensagem =
                            "Essa conta não existe.";
                        break;


                    case "auth/wrong-password":
                        mensagem =
                            "Palavra-passe incorreta.";
                        break;


                    case "auth/too-many-requests":
                        mensagem =
                            "Muitas tentativas. Tenta novamente mais tarde.";
                        break;


                    case "auth/network-request-failed":
                        mensagem =
                            "Erro de rede.";
                        break;


                    case "auth/operation-not-allowed":
                        mensagem =
                            "O login por e-mail ainda não está ativado no Firebase.";
                        break;


                    default:
                        mensagem =
                            erro.message ||
                            mensagem;

                }


                mostrarMensagem(
                    mensagem,
                    true
                );

            } finally {

                carregando(false);

            }

        }
    );

}


/* =====================================================
   VERIFICAR SESSÃO FIREBASE
   ===================================================== */

onAuthStateChanged(
    auth,
    user => {

        if (user) {

            console.log(
                "Firebase:",
                user.email
            );

        } else {

            console.log(
                "Nenhum utilizador Firebase autenticado."
            );

        }

    }
);
