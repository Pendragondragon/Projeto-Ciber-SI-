const editBtn = document.getElementById('edit-toggle-btn');
const saveActions = document.getElementById('save-actions');
const form = document.getElementById('profile-form');
const inputs = form.querySelectorAll('.input-field, #file-upload');
const imageWrapper = document.getElementById('image-wrapper');
const fileInput = document.getElementById('file-upload');

// Toggle Edit Mode
editBtn.addEventListener('click', () => {
    const isEditing = editBtn.classList.contains('editing');

    if (!isEditing) {
        // Switch to Edit Mode
        inputs.forEach(input => input.disabled = false);
        imageWrapper.classList.remove('is-locked');
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
    if (!imageWrapper.classList.contains('is-locked')) {
        fileInput.click();
    }
});

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
