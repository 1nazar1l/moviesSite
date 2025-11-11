document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatarInput');
    const avatarForm = document.getElementById('avatarForm');
    
    if (avatarInput && avatarForm) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // Автоматически отправляем форму
                avatarForm.submit();
            }
        });
    }

    const addListButton = document.querySelector("#add-list-button")
    const addListForm = document.querySelector(".add-list-form")
    addListButton.addEventListener("click", () => {
        addListButton.classList.add("active")
        addListForm.classList.add("active")
    })
});