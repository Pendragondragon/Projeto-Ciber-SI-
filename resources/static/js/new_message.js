const url = "/message";

document.addEventListener("DOMContentLoaded", async () => {
    const methodSelect = document.getElementById('method');
    const rsa_bits = document.getElementById('rsaDiv');
    const rsaSelect = document.getElementById('rsa_bits');

    const pass = document.getElementById('passDiv');
    const passInput = document.getElementById('pass');

    const whichkeyDiv = document.getElementById('whichKeyDiv');
    const whichAlgSim = document.getElementById('algSimDiv');
    const yesKey = document.getElementById('yes_nova');
    const noKey = document.getElementById('no_nova');
    const algSim_bits = document.getElementById('algSim_bits');

    const chosenRandDiv = document.getElementById('chosenRandDiv');
    const passRand = document.getElementById('passRand');
    const passChosen = document.getElementById('passChosen');

    const BtnCreateVault = document.getElementById('createVault');

    //como a opcao default nao contem nenhuma opcional
    //como default podemos esconder tudo
    function setMethodOptions() {
        const selectedValue = methodSelect.value;

        //esconde todos os que sao opcionais
        [rsaDiv, whichKeyDiv, chosenRandDiv, algSimDiv, pass].forEach(div => {
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
    }

    setMethodOptions();

    BtnCreateVault.addEventListener("click", async (e) => {
        e.preventDefault();
        //por ser um form

        const form = document.querySelector('form');
        if (!form.reportValidity()) return;
        const formData = new FormData(form);

        //os campos escondidos vão ser null, se estiverem escondidos
        //entao podemos mandar todos juntos
        const payload = {
            title: formData.get('title'),
            message: formData.get('message'),
            method: formData.get('method'),
            password: formData.get('pass'),
            hmac_hash: formData.get('sig_hash'),
            sig_hash: formData.get('hash_signature'),
            rsa_bits: formData.get('rsa_bits')
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
                    mostrarNotificacao('Vault created successfully!', 'success');

                    setTimeout(() => {
                        window.location.href = "/deposit";
                    }, 1500);
                } else {
                    const mensagem = data.message || data.error || 'Invalid Values.';
                    mostrarNotificacao(mensagem, 'error');
                }
            });
    });

    //mostra só as opçoes possiveis de cada metodo
    methodSelect.addEventListener("change", setMethodOptions);
    passRand.addEventListener('change', setMethodOptions);
    passChosen.addEventListener('change', setMethodOptions);

});

