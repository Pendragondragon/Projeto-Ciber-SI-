//alterar o url para estar certo
const url = "/auth";

document.getElementById('registo-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    const spinner = document.getElementById('loadingSpinner');

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

    if (spinner) {
        spinner.classList.remove('hidden');
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
                if (spinner) {
                    spinner.classList.add('hidden');
                }
                // se a chave privada foi gerada pelo servidor, mostrar o modal estilo "new_message"
                if (data.private_key) {
                    mostrarNotificacao('Registo bem sucedido! Guarde a sua chave privada.', 'success');
                    // criar modal similar ao usado em new_message.js
                    (function showRsaPopup(privateKey, user_id, fallbackMessage) {
                        return new Promise((resolve) => {
                            const overlay = document.createElement('div');
                            overlay.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4';

                            const modal = document.createElement('div');
                            modal.className = 'w-full max-w-2xl rounded-lg bg-gray-800 p-6 text-white shadow-xl';

                            const title = document.createElement('h2');
                            title.className = 'mb-3 text-xl font-semibold';
                            title.textContent = privateKey ? 'Guarde a sua chave privada' : 'Chave privada';

                            const idBadge = document.createElement('div');
                            idBadge.className = 'mb-4 inline-block rounded border border-indigo-500/30 bg-indigo-500/10 px-2 py-1 text-xs font-mono font-bold tracking-wider text-indigo-400';
                            idBadge.textContent = user_id ? `User id: #${user_id}` : '';

                            const description = document.createElement('p');
                            description.className = 'mb-4 text-sm text-gray-200';

                            const actions = document.createElement('div');
                            actions.className = 'mt-4 flex justify-end gap-3';

                            const closeButton = document.createElement('button');
                            closeButton.type = 'button';
                            closeButton.className = 'rounded-md bg-gray-600 px-4 py-2 text-sm font-semibold hover:bg-gray-500';
                            closeButton.textContent = 'Fechar';
                            closeButton.addEventListener('click', () => {
                                overlay.remove();
                                resolve();
                                window.location.href = '/login';
                            });

                            if (privateKey) {
                                description.textContent = fallbackMessage || 'Guarde esta chave privada num local seguro. Vai precisar dela para entrar na sua conta.';

                                const keyBox = document.createElement('textarea');
                                keyBox.className = 'h-56 w-full rounded-md bg-gray-900 p-3 text-xs text-green-200 outline-none';
                                keyBox.readOnly = true;
                                keyBox.value = privateKey;

                                const copyButton = document.createElement('button');
                                copyButton.type = 'button';
                                copyButton.className = 'rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold hover:bg-indigo-500';
                                copyButton.textContent = 'Copiar chave';
                                copyButton.addEventListener('click', async () => {
                                    try {
                                        await navigator.clipboard.writeText(privateKey);
                                        mostrarNotificacao('Chave privada copiada!', 'success');
                                    } catch (error) {
                                        mostrarNotificacao('Nao foi possivel copiar a chave.', 'error');
                                    }
                                });

                                const downloadButton = document.createElement('button');
                                downloadButton.type = 'button';
                                downloadButton.className = 'rounded-md bg-green-600 px-4 py-2 text-sm font-semibold hover:bg-green-500';
                                downloadButton.textContent = 'Download chave';
                                downloadButton.addEventListener('click', () => {
                                    const blob = new Blob([privateKey], { type: 'text/plain' });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = 'private_key.pem';
                                    document.body.appendChild(a);
                                    a.click();
                                    document.body.removeChild(a);
                                    URL.revokeObjectURL(url);
                                    mostrarNotificacao('Chave privada descarregada!', 'success');
                                });

                                actions.appendChild(copyButton);
                                actions.appendChild(downloadButton);
                                modal.appendChild(title);
                                if (user_id) modal.appendChild(idBadge);
                                modal.appendChild(description);
                                modal.appendChild(keyBox);
                            } else {
                                description.textContent = fallbackMessage || 'Espero que nao tenha perdido a sua chave privada.';
                                modal.appendChild(title);
                                modal.appendChild(description);
                            }

                            actions.appendChild(closeButton);
                            modal.appendChild(actions);
                            overlay.appendChild(modal);
                            document.body.appendChild(overlay);
                        });
                    })(data.private_key, data.user_id, data.private_key_message);
                } else {
                    mostrarNotificacao('Successful Sign In!', 'success');
                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 1500);
                }
            } else {
                if (spinner) {
                    spinner.classList.add('hidden');
                }
                const mensagem = data.message || data.error || 'Invalid Values.';
                mostrarNotificacao(mensagem, 'error');
            }
        })
        .catch(() => {
            if (spinner) {
                spinner.classList.add('hidden');
            }
            mostrarNotificacao('Nao foi possivel concluir o registo.', 'error');
        });
});
