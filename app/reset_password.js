document.getElementById('reset-password-form').addEventListener('submit', function (event) {
    event.preventDefault();

    // Extrair o token do URL (?token=xyz)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        mostrarNotificacao('As passwords não coincidem.', 'error');
        return;
    }

    if (!token) {
        mostrarNotificacao('Token em falta. Use o link do email.', 'error');
        return;
    }

    fetch('/auth/reset-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacao('Password atualizada com sucesso!', 'success');
            setTimeout(() => { window.location.href = '/login'; }, 2000);
        } else {
            mostrarNotificacao(data.error || 'Erro ao redefinir password.', 'error');
        }
    })
    .catch(error => {
        mostrarNotificacao('Erro na ligação ao servidor.', 'error');
    });
});
