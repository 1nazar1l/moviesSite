document.addEventListener('DOMContentLoaded', () => {
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const confirmPasswordInput = document.getElementById('confirm-password');
    
    toggleConfirmPassword.addEventListener('click', () => {
        const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        confirmPasswordInput.setAttribute('type', type);
        
        const icon = toggleConfirmPassword.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });

    const regForm = document.getElementById('regForm');
    
    regForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const nickname = document.getElementById('nickname').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        console.log(email)
        console.log(nickname)
        console.log(password)
        console.log(confirmPassword)
        
        if (password != confirmPassword) {
            alert('Пароли не совпадают')
        }
        else {
            // Здесь должна быть логика отправки данных на сервер
            
            // Временная имитация успешного входа
            alert('Вход выполнен успешно!');
            window.location.href = 'index.html';
        }
    });
    
    // Обработка кнопок социальных сетей
    document.querySelectorAll('.social-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            alert('Функция входа через социальные сети будет реализована позже');
        });
    });
})
