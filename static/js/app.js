document.addEventListener("DOMContentLoaded", function () {


    const password = document.getElementById("password");

    const showPassword = document.getElementById("showPassword");



    if (password && showPassword) {


        showPassword.addEventListener("click", function () {



            if (password.type === "password") {


                password.type = "text";

                showPassword.innerHTML = "🙈";


            } else {


                password.type = "password";

                showPassword.innerHTML = "👁️";


            }


        });


    }


});