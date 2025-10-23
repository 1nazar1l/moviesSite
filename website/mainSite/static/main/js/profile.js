document.addEventListener('DOMContentLoaded', () => {
    const removeFavoriteBtns = document.querySelectorAll('.remove-favorite');
    const favoritesGrid = document.getElementById('favoritesGrid');
    const emptyFavorites = document.getElementById('emptyFavorites');
    const favoritesCount = document.getElementById('favoritesCount');

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
    
