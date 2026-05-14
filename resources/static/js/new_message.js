const url = "/message";

function showRsaPopup(privateKey, vault_id, fallbackMessage) {
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
        idBadge.textContent = `Vault id: #${vault_id}`;

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
        });

        if (privateKey) {
            description.textContent = 'Guarde esta chave privada num local seguro. Vai precisar dela para abrir o cofre.';

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
            modal.appendChild(idBadge); 
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
}

document.addEventListener("DOMContentLoaded", async () => {
    const methodSelect = document.getElementById('method');
    const rsaDiv = document.getElementById('rsaDiv');
    const rsaSelect = document.getElementById('rsa_bits');

    const passDiv = document.getElementById('passDiv');
    const passInput = document.getElementById('pass');

    const whichKeyDiv = document.getElementById('whichKeyDiv');
    const algSimDiv = document.getElementById('algSimDiv');
    const yesKey = document.getElementById('yes_nova');
    const noKey = document.getElementById('no_antiga');
    const algSim_bits = document.getElementById('algSim_bits');

    const chosenRandDiv = document.getElementById('chosenRandDiv');
    const passRand = document.getElementById('passRand');
    const passChosen = document.getElementById('passChosen');

    const BtnCreateVault = document.getElementById('createVault');

    const messageArea = document.getElementById('message');
    const limitDisplay = document.getElementById('limit');
    const currentDisplay = document.getElementById('current');

    //como cada rsa size tem um tamanho especifico de caracteres temos um listener para mudar quando se mudar o tamanho rsa
    function updateLimit() {
        const selectedValue = methodSelect.value;
        let newLimit;

        //como cifras simetricas nao tem limite, podemos por um numero grande
        //so ter cuidado paranao demorar muito tempo
        if (selectedValue == "random-key") {
            newLimit = 10000;
        } else {
            const bits = parseInt(rsaSelect.value) || 2048;

            newLimit = (bits / 8) - 11;
        }

        messageArea.setAttribute('maxlength', newLimit);

        limitDisplay.textContent = newLimit;

        if (messageArea.value.length > newLimit) {
            messageArea.value = messageArea.value.substring(0, newLimit);
            currentDisplay.textContent = newLimit;
            mostrarNotificacao('Max number of characters achieved!', 'success');
        }
    }

    //como a opcao default nao contem nenhuma opcional
    //como default podemos esconder tudo
    function setMethodOptions() {
        const selectedValue = methodSelect.value;

        //esconde todos os que sao opcionais
        [rsaDiv, whichKeyDiv, chosenRandDiv, algSimDiv, passDiv].forEach(div => {
            if (div) div.style.display = "none";
        });

        // Remove a obrigatoriedade
        const allInputs = [rsaSelect, yesKey, noKey, algSim_bits, passRand, passChosen, passInput];
        allInputs.forEach(input => {
            if (input) input.removeAttribute('required');
        });


        //mostra so os que interessam
        if (selectedValue === "rsa") {
            if (rsaDiv) rsaDiv.style.display = "block";
            if (rsaSelect) rsaSelect.setAttribute('required', '');

            if (whichKeyDiv) whichKeyDiv.style.display = "block";
            if (yesKey) yesKey.setAttribute('required', '');
            if (noKey) noKey.setAttribute('required', '');

        } else if (selectedValue === "random-key") {
            if (algSimDiv) algSimDiv.style.display = "block";
            if (algSim_bits) algSim_bits.setAttribute('required', '');

            if (chosenRandDiv) chosenRandDiv.style.display = "block";
            if (passChosen) passChosen.setAttribute('required', '');
            if (passRand) passRand.setAttribute('required', '');

            if (passChosen && passChosen.checked) {
                if (passDiv) passDiv.style.display = "block";
                if (passInput) passInput.setAttribute('required', '');
            }
        }

        updateLimit();
    }

    setMethodOptions();

    BtnCreateVault.addEventListener("click", async (e) => {
        e.preventDefault();
        //por ser um form

        const spinner = document.getElementById("loadingSpinner");

        spinner.classList.remove("hidden");

        const form = document.querySelector('form');
        if (!form.reportValidity()) {
            spinner.classList.add("hidden");
            return;
        }
        const formData = new FormData(form);

        //os campos escondidos vão ser null, se estiverem escondidos
        //entao podemos mandar todos juntos
        const payload = {
            title: formData.get('title'),
            message: formData.get('message'),
            method: formData.get('method'),

            algSim_bits: formData.get('algSim_bits'),
            symmetric_key_source: formData.get('symmetric_key_source'),
            password: formData.get('pass'),

            rsa_bits: formData.get('rsa_bits'),
            rsa_key_type: formData.get('rsa_key_type'),

            hmac_hash: formData.get('sig_hash'),
            sig_hash: formData.get('hash_signature')
        };

        fetch(url + '/deposit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    spinner.classList.add("hidden");
                    if (payload.method === 'rsa') {
                        showRsaPopup(data.private_key, data.vault_id, 'Vault created successfully!').then(() => {
                            window.location.href = "/deposit";
                        });
                    }

                    mostrarNotificacao('Vault created successfully!', 'success');
                } else {
                    spinner.classList.add("hidden");
                    const mensagem = data.message || data.error || 'Invalid Values.';
                    mostrarNotificacao(mensagem, 'error');
                }
            })
            .catch(() => {
                spinner.classList.add("hidden");
                mostrarNotificacao('Nao foi possivel criar o vault.', 'error');
            });
    });

    //mostra só as opçoes possiveis de cada metodo
    methodSelect.addEventListener("change", setMethodOptions);
    passRand.addEventListener('change', setMethodOptions);
    passChosen.addEventListener('change', setMethodOptions);

    //limite de chars a inserir
    rsaSelect.addEventListener('change', updateLimit);

    messageArea.addEventListener('input', () => {
        currentDisplay.textContent = messageArea.value.length;
    });

});
