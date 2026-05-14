const editBtn = document.getElementById('edit-toggle-btn');
const saveActions = document.getElementById('save-actions');
const form = document.getElementById('profile-form');

const realInputs = form.querySelectorAll('#uname , #email')
const jokeFields = form.querySelectorAll('#fname , #lname , #story');
const imageWrapper = document.getElementById('image-wrapper');
//const fileInput = document.getElementById('file-upload');

// Toggle Edit Mode
editBtn.addEventListener('click', () => {
    const isEditing = editBtn.classList.contains('editing');

    if (!isEditing) {
        // Switch to Edit Mode: ONLY FOR EMAIL AND USERNAME
        realInputs.forEach(input => input.disabled = false);

        saveActions.style.display = 'flex';
        editBtn.innerHTML = '<i class="fa-solid fa-xmark"></i> Exit Editing';
        editBtn.classList.add('editing');
    } else {
        // Exit Edit Mode (Reload to discard changes)
        window.location.reload();
    }
});

// Allow image click ONLY if not locked
imageWrapper.addEventListener('click', () => {
    const isEditing = editBtn.classList.contains('editing');
    if (isEditing){
        mostrarNotificacao("You can't change your appearance, Anakin", 'error');
    }
});


jokeFields.forEach(field => {
    field.parentElement.addEventListener('click', () => {
        const isEditing = editBtn.classList.contains('editing');
        if (isEditing && field.disabled) {
            mostrarNotificacao("The Jedi Biometric Security forbids this action.", 'error');
        }
    })
}

)
// Image Preview Function
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
        const output = document.getElementById('profile-preview');
        output.src = reader.result;
    };
    if(event.target.files[0]) {
        reader.readAsDataURL(event.target.files[0]);
    }
}
