const methodSelect = document.getElementById('method');
const rsa_bits = document.getElementById('rsaDiv');
const pass = document.getElementById('passDiv');

const BtnCreateVault = document.getElementById('createVault');

document.addEventListener("DOMContentLoaded", async () => {
    setMethodOptionsReset();
});

BtnCreateVault.addEventListener("click", async () => {
    const title = document.getElementById('title');
    const message = document.getElementById('message');
});

//mostra só as opçoes possiveis de cada metodo
methodSelect.addEventListener("change", () => {
    const selectedValue = methodSelect.value;

    //esconde todos os que sao opcionais
    rsa_bits.style.display = "none";
    pass.style.display = "none";

    //mostra so os que interessam
    if (selectedValue === "rsa") {
        rsa_bits.style.display = "block";
    } else if (selectedValue === "password") {
        pass.style.display = "block";
    }
});

//como a opcao default nao contem nenhuma opcional
//como default podemos esconder tudo
function setMethodOptionsReset(){
    rsa_bits.style.display = "none";
    pass.style.display = "none";
}