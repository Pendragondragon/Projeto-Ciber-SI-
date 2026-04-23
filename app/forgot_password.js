document.getElementById('forgot-password-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;

    if (!email) {
        mostrarNotificacao('Por favor, insira o seu email.', 'error');
        return;
    }

    fetch('/auth/request-reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacao('Email de recuperação enviado com sucesso!', 'success');
        } else {
            mostrarNotificacao(data.error || 'Erro ao processar o pedido.', 'error');
        }
    })
    .catch(error => {
        mostrarNotificacao('Erro na ligação ao servidor.', 'error');
    });
});
