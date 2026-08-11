import {
initializeApp
} from "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";

import {
getAuth,
GoogleAuthProvider,
signInWithPopup,
signInWithEmailAndPassword,
createUserWithEmailAndPassword,
updateProfile,
sendEmailVerification
} from "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";

const firebaseConfig = {

```
apiKey: "AIzaSyA9tQ1MHU9M6bQc8zSpYSkVRQRaMIX1YNU",

authDomain: "mello-ia.firebaseapp.com",

projectId: "mello-ia",

storageBucket: "mello-ia.firebasestorage.app",

messagingSenderId: "233987997050",

appId: "1:233987997050:web:c0dda63bff6c5f60aa2ac3",

measurementId: "G-Z65WXNRNQS"
```

};

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);

const googleProvider =
new GoogleAuthProvider();

function mostrarMensagem(
mensagem,
erro = false
) {

```
const elemento =
    document.getElementById(
        "auth-message"
    );

if (!elemento) {
    return;
}

elemento.textContent =
    mensagem;

elemento.className =
    erro
        ? "auth-message error"
        : "auth-message success";
```

}

async function enviarTokenParaServidor(
user
) {

```
const token =
    await user.getIdToken();

const resposta =
    await fetch(
        "/auth/firebase",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                idToken: token
            })
        }
    );


const data =
    await resposta.json();


if (!resposta.ok) {

    throw new Error(
        data.error ||
        "Não foi possível autenticar no servidor."
    );

}


window.location.href = "/";
```

}

const googleLogin =
document.getElementById(
"google-login"
);

if (googleLogin) {

```
googleLogin.addEventListener(
    "click",
    async () => {

        try {

            mostrarMensagem(
                "A abrir o Google..."
            );

            const resultado =
                await signInWithPopup(
                    auth,
                    googleProvider
                );

            await enviarTokenParaServidor(
                resultado.user
            );

        } catch (erro) {

            console.error(
                erro
            );

            mostrarMensagem(
                traduzirErroFirebase(
                    erro
                ),
                true
            );

        }

    }
);
```

}

const googleRegister =
document.getElementById(
"google-register"
);

if (googleRegister) {

```
googleRegister.addEventListener(
    "click",
    async () => {

        try {

            mostrarMensagem(
                "A abrir o Google..."
            );

            const resultado =
                await signInWithPopup(
                    auth,
                    googleProvider
                );

            await enviarTokenParaServidor(
                resultado.user
            );

        } catch (erro) {

            console.error(
                erro
            );

            mostrarMensagem(
                traduzirErroFirebase(
                    erro
                ),
                true
            );

        }

    }
);
```

}

const loginForm =
document.getElementById(
"login-form"
);

if (loginForm) {

```
loginForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const email =
            document
                .getElementById(
                    "email"
                )
                .value
                .trim();


        const password =
            document
                .getElementById(
                    "password"
                )
                .value;


        try {

            mostrarMensagem(
                "A entrar..."
            );


            const resultado =
                await signInWithEmailAndPassword(
                    auth,
                    email,
                    password
                );


            await enviarTokenParaServidor(
                resultado.user
            );


        } catch (erro) {

            console.error(
                erro
            );

            mostrarMensagem(
                traduzirErroFirebase(
                    erro
                ),
                true
            );

        }

    }
);
```

}

const registerForm =
document.getElementById(
"register-form"
);

if (registerForm) {

```
registerForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const name =
            document
                .getElementById(
                    "name"
                )
                .value
                .trim();


        const email =
            document
                .getElementById(
                    "email"
                )
                .value
                .trim();


        const password =
            document
                .getElementById(
                    "password"
                )
                .value;


        try {

            mostrarMensagem(
                "A criar a sua conta..."
            );


            const resultado =
                await createUserWithEmailAndPassword(
                    auth,
                    email,
                    password
                );


            await updateProfile(
                resultado.user,
                {
                    displayName: name
                }
            );


            try {

                await sendEmailVerification(
                    resultado.user
                );

            } catch (erroEmail) {

                console.warn(
                    "Não foi possível enviar a verificação:",
                    erroEmail
                );

            }


            await enviarTokenParaServidor(
                resultado.user
            );


        } catch (erro) {

            console.error(
                erro
            );

            mostrarMensagem(
                traduzirErroFirebase(
                    erro
                ),
                true
            );

        }

    }
);
```

}

function traduzirErroFirebase(
erro
) {

```
const codigo =
    erro?.code || "";


const mensagens = {

    "auth/invalid-email":
        "O endereço de e-mail não é válido.",

    "auth/user-not-found":
        "Não encontramos uma conta com este e-mail.",

    "auth/wrong-password":
        "A palavra-passe está incorreta.",

    "auth/invalid-credential":
        "E-mail ou palavra-passe incorretos.",

    "auth/email-already-in-use":
        "Este e-mail já está registado.",

    "auth/weak-password":
        "A palavra-passe é demasiado fraca.",

    "auth/popup-closed-by-user":
        "A janela do Google foi fechada.",

    "auth/popup-blocked":
        "O navegador bloqueou a janela do Google.",

    "auth/too-many-requests":
        "Foram feitas muitas tentativas. Tente novamente mais tarde.",

    "auth/network-request-failed":
        "Problema de conexão com a Internet."

};


return mensagens[codigo] ||
    "Não foi possível concluir a autenticação.";
```

}
