//alterar o url para estar certo
const url = "/auth";

document.addEventListener('DOMContentLoaded', function () {
    isLoggedIn();
});

document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // validacao
    if (!email || !password) {
        alert('It has to insert email and password.');
        return;
    }

    // iniciar pedido de login
    fetch(url + '/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ email, password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarNotificacao('Successful Login!', 'success');

                setTimeout(() => {
                    window.location.href = "/index";
                }, 1500);
            } else {
                const mensagem = data.message || data.error || 'Invalid Values.';
                mostrarNotificacao(mensagem, 'error');
            }
        })
        .catch(error => {
            console.error('Error in login:', error);
            alert('There was an error in login. Please try again later.');
        });
});

//verifica se já está logged in para redirecionar para o inicio
//vai fazer um pedido e se receber alguma resposta de volta quer dizer que
//foi validado pelo middleware -> token valido
//e que existe na base de dados -> vem com dados associados
function isLoggedIn() {
    fetch('/auth/check', {
        //manda o jwt token atraves de httponly cookies
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            if (data.isLoggedIn) {
                window.location.href = "/index";
            }
        })
}
