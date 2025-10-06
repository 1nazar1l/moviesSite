document.addEventListener('DOMContentLoaded', () => {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    togglePassword.addEventListener('click', () => {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = togglePassword.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
    
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const confirmPasswordInput = document.getElementById('confirm-password');
    
    toggleConfirmPassword.addEventListener('click', () => {
        const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        confirmPasswordInput.setAttribute('type', type);
        
        const icon = toggleConfirmPassword.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });

    const usernameInput = document.getElementById('usernameInput')
    console.log(usernameInput.value)

    function checkPasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (password === '' || confirmPassword === '') {
            return false;
        }
        
        if (password === confirmPassword) {
            return true;
        } else {
            return false;
        }
    }

    function checkUsernameMatch() {
        const username = usernameInput.value
        if (username.length < 5) {
            alert("Никнейм слишком короткий")
            return false
        }
        else if (username.length > 11) {
            alert("Никнейм слишком длинный")
            return false
        }
        else {
            return true
        }
    }

    const regForm = document.getElementById('regForm');

    regForm.addEventListener('submit', function(event) {
        if (!checkPasswordMatch()) {
            event.preventDefault();
            alert('Пожалуйста, убедитесь, что пароли совпадают');
        }
        else if(!checkUsernameMatch(event)) {
            event.preventDefault();
        }
    });
    
    // Обработка кнопок социальных сетей
    document.querySelectorAll('.social-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            alert('Функция входа через социальные сети будет реализована позже');
        });
    });
})
