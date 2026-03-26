//alterar o url para estar certo
const url = "/auth";

document.addEventListener('DOMContentLoaded', function () {
   isLoggedIn();
});

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // validacao
    if (!email || !password) {
        alert('Tem de inserir o email e a password.');
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
            mostrarNotificacao('Login efetuado com sucesso!', 'sucesso');
            
            setTimeout(() => {
                window.location.href = "/inicio.html";
            }, 1500);
        } else {
            const mensagem = data.message || data.error || 'Credenciais inválidas.';
            mostrarNotificacao(mensagem, 'erro');
        }
    })
    .catch(error => {
        console.error('Erro durante o login:', error);
        alert('Ocorreu um erro durante o login. Por favor, tente novamente mais tarde.');
    });
});

//verifica se já está logged in para redirecionar para o inicio
//vai fazer um pedido e se receber alguma resposta de volta quer dizer que
//foi validado pelo middleware -> token valido
//e que existe na base de dados -> vem com dados associados
function isLoggedIn(){
    fetch(url + '/check', {
        //manda o jwt token atraves de httponly cookies
        credentials: 'include' 
    })
    .then(response => response.json())
    .then(data => {
        if (data.isLoggedIn) {
            window.location.href = "/inicio.html";
        }
    })
}