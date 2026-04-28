//alterar o url para estar certo
const url = "/auth";

document.getElementById('registo-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmpassword = document.getElementById('confirmpassword').value;

    // validacao
    if (!username || !email || !password || !confirmpassword) {
        alert('Please insert all the information requested.');
        return;
    }

    if (!(password === confirmpassword)) {
        alert('Passwords dont match.');
        return;
    }

    // iniciar pedido de registo
    fetch(url + '/registerUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ username, email, password })
    })
        .then(response => {
            console.log("Status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Data:", data);
            if (data.success) {
                mostrarNotificacao('Successful Sign In!', 'success');
                setTimeout(() => {
                    window.location.href = "/login";
                }, 1500);
            } else {
                const mensagem = data.message || data.error || 'Invalid Values.';
                mostrarNotificacao(mensagem, 'error');
            }
        });
});
