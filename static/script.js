/* =====================================================
   MELLO IA
   SPLASH SCREEN CONTROLLER
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const splash =
        document.getElementById("splash");

    const enterButton =
        document.getElementById("enterButton");


    /*
     * Entrar manualmente
     */

    enterButton.addEventListener("click", () => {

        openMello();

    });


    /*
     * Entrada automática
     *
     * Depois de aproximadamente 5 segundos
     */

    setTimeout(() => {

        openMello();

    }, 5500);


    function openMello() {

        if (splash.classList.contains("hide")) {
            return;
        }

        splash.classList.add("hide");

        /*
         * Depois da animação,
         * removemos a splash completamente.
         */

        setTimeout(() => {

            splash.style.display = "none";

            document.body.style.overflow = "auto";

        }, 900);

    }

});
