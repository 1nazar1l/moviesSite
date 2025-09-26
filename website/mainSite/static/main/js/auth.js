document.addEventListener('DOMContentLoaded', () => {
    // Переключение видимости пароля
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    togglePassword.addEventListener('click', () => {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = togglePassword.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
    
    // Обработка формы авторизации
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;
        
        // Здесь должна быть логика отправки данных на сервер
        console.log('Попытка входа:', { email, password, remember });
        
        // Временная имитация успешного входа
        alert('Вход выполнен успешно!');
        window.location.href = 'index.html';
    });
    
    // Обработка кнопок социальных сетей
    document.querySelectorAll('.social-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            alert('Функция входа через социальные сети будет реализована позже');
        });
    });
})
