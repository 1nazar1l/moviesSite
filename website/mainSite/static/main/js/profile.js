document.addEventListener('DOMContentLoaded', () => {
    // Функциональность профиля
    const editAvatarBtn = document.getElementById('editAvatar');
    const userAvatar = document.getElementById('userAvatar');
    const saveChangesBtn = document.getElementById('saveChangesBtn');
    const cancelChangesBtn = document.getElementById('cancelChangesBtn');
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    const removeFavoriteBtns = document.querySelectorAll('.remove-favorite');
    const favoritesGrid = document.getElementById('favoritesGrid');
    const emptyFavorites = document.getElementById('emptyFavorites');
    const favoritesCount = document.getElementById('favoritesCount');

    // Смена аватара
    editAvatarBtn.addEventListener('click', () => {
        const colors = ['#2563EB', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        userAvatar.style.background = `linear-gradient(135deg, ${randomColor}, ${randomColor}80)`;
    });

    // Сохранение изменений профиля
    saveChangesBtn.addEventListener('click', () => {
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        
        document.getElementById('userName').textContent = username;
        document.getElementById('userEmail').textContent = email;
        
        alert('Изменения профиля сохранены!');
    });

    // Отмена изменений
    cancelChangesBtn.addEventListener('click', () => {
        document.getElementById('username').value = 'Киноман007';
        document.getElementById('email').value = 'kinoman@moviemarks.ru';
        document.getElementById('bio').value = 'Любитель качественного кино, особенно научной фантастики и драмы. Смотрю фильмы каждый вечер!';
    });

    // Смена пароля
    changePasswordBtn.addEventListener('click', () => {
        alert('Функция смены пароля будет доступна в следующем обновлении!');
    });

    // Удаление из избранного
    removeFavoriteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const movieCard = btn.closest('.movie-card');
            movieCard.style.opacity = '0';
            
            setTimeout(() => {
                movieCard.remove();
                updateFavoritesCount();
                
                // Показываем сообщение, если избранное пусто
                if (favoritesGrid.children.length === 0) {
                    emptyFavorites.style.display = 'block';
                }
            }, 300);
        });
    });

    // Обновление счетчика избранного
    function updateFavoritesCount() {
        const currentCount = parseInt(favoritesCount.textContent);
        favoritesCount.textContent = currentCount - 1;
    }
    
    // Проверяем, есть ли избранные фильмы
    if (favoritesGrid.children.length === 0) {
        emptyFavorites.style.display = 'block';
    }
});
    
