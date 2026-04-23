const methodSelect = document.getElementById('method');
const rsa_bits = document.getElementById('rsaDiv');
const pass = document.getElementById('passDiv');

document.addEventListener("DOMContentLoaded", async () => {
    setMethodOptionsReset();
});

methodSelect.addEventListener("change", () => {
    const selectedValue = methodSelect.value;

    rsa_bits.style.display = "none";
    pass.style.display = "none";

    if (selectedValue === "rsa") {
        rsa_bits.style.display = "block";
    } else if (selectedValue === "password") {
        pass.style.display = "block";
    }
});

function setMethodOptionsReset(){
    rsa_bits.style.display = "none";
    pass.style.display = "none";
}