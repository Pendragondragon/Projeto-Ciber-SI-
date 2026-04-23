const url = "/message";

document.addEventListener("DOMContentLoaded", async () => {
    setMethodOptionsReset();
    const methodSelect = document.getElementById('method');
    const rsa_bits = document.getElementById('rsaDiv');
    const pass = document.getElementById('passDiv');
    const passInput = document.getElementById('pass');
    const rsaSelect = document.getElementById('rsa_bits');

    const BtnCreateVault = document.getElementById('createVault');

    BtnCreateVault.addEventListener("click", async () => {
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
    methodSelect.addEventListener("change", () => {
        const selectedValue = methodSelect.value;

        //esconde todos os que sao opcionais
        rsa_bits.style.display = "none";
        pass.style.display = "none";

        //remove a obrigatoriedade
        passInput.removeAttribute('required');
        rsaSelect.removeAttribute('required');

        //mostra so os que interessam
        if (selectedValue === "rsa") {
            rsa_bits.style.display = "block";
            rsaSelect.setAttribute('required', '');
        } else if (selectedValue === "password") {
            pass.style.display = "block";
            passInput.setAttribute('required', '');
        }
    });


});

//como a opcao default nao contem nenhuma opcional
//como default podemos esconder tudo
function setMethodOptionsReset() {
    rsa_bits.style.display = "none";
    pass.style.display = "none";
}