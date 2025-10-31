document.addEventListener('DOMContentLoaded', () => {
    // Элементы DOM
    const elements = {
        togglePassword: document.getElementById('togglePassword'),
        passwordInput: document.getElementById('password'),
        toggleConfirmPassword: document.getElementById('toggleConfirmPassword'),
        confirmPasswordInput: document.getElementById('confirm-password'),
        passwordError: document.querySelector('.password-error'),
        usernameError: document.querySelector('.username-error'),
        passwordRating: document.getElementById('passwordRating'),
        regForm: document.getElementById('regForm'),
        usernameInput: document.getElementById('usernameInput')
    };

    // Функции для проверки пароля
    const passwordChecks = {
        hasDigit: (password) => /\d/.test(password),
    };

    // Универсальная функция переключения видимости пароля
    function setupPasswordToggle(toggleButton, passwordInput) {
        toggleButton.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = toggleButton.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    // Настройка переключения видимости паролей
    setupPasswordToggle(elements.togglePassword, elements.passwordInput);
    setupPasswordToggle(elements.toggleConfirmPassword, elements.confirmPasswordInput);

    // Проверка совпадения паролей
    function checkPasswordMatch() {
        const { passwordInput, confirmPasswordInput } = elements;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (password === '' || confirmPassword === '') {
            return false;
        }
        
        return password === confirmPassword;
    }

    // Проверка имени пользователя
    function checkUsernameMatch() {
        const username = elements.usernameInput.value;
        return username.length >= 5 && username.length <= 50;
    }

    // Валидация формы
    function validateForm(event) {
        let isValid = true;
        const password = elements.passwordInput.value;
        
        // Сброс ошибок
        elements.passwordError.classList.remove('active');
        elements.usernameError.classList.remove('active');
        
        // Проверка имени пользователя
        if (!checkUsernameMatch()) {
            elements.usernameError.classList.add('active');
            isValid = false;
        }
        
        // Проверка совпадения паролей
        if (!checkPasswordMatch()) {
            elements.passwordError.textContent = "Пароли не совпадают";
            elements.passwordError.classList.add('active');
            isValid = false;
        }
        
        // Проверка на символы
        if (passwordChecks.hasSymbols(password)) {
            elements.passwordError.textContent = "Пароль должен состоять только из букв и цифр";
            elements.passwordError.classList.add('active');
            isValid = false;
        }
        
        if (!isValid && event) {
            event.preventDefault();
        }
        
        return isValid;
    }
    
    elements.regForm.addEventListener('submit', validateForm);
    
    // Обработка кнопок социальных сетей
    document.querySelectorAll('.social-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            alert('Функция входа через социальные сети будет реализована позже');
        });
    });
});