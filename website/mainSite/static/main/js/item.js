document.addEventListener('DOMContentLoaded', () => {
      // Добавление в избранное
      const addToFavoritesBtn = document.getElementById('addToFavorites');
      let isInFavorites = false;
      
      addToFavoritesBtn.addEventListener('click', () => {
        isInFavorites = !isInFavorites;
        
        if (isInFavorites) {
          addToFavoritesBtn.innerHTML = '<i class="fas fa-bookmark"></i> В избранном';
          addToFavoritesBtn.style.backgroundColor = '#10B981';
          addToFavoritesBtn.style.color = 'white';
        } else {
          addToFavoritesBtn.innerHTML = '<i class="far fa-bookmark"></i> В избранное';
          addToFavoritesBtn.style.backgroundColor = '';
          addToFavoritesBtn.style.color = '';
        }
      });
      
      // Воспроизведение трейлера (заглушка)
      document.querySelector('.btn-primary').addEventListener('click', () => {
        alert('Трейлер будет воспроизведен в модальном окне');
      });

      // Функциональность комментариев
      const submitCommentBtn = document.getElementById('submitComment');
      const commentText = document.getElementById('commentText');
      const commentRating = document.getElementById('commentRating');
      const commentsList = document.getElementById('commentsList');
      const commentsCount = document.getElementById('commentsCount');
      const noComments = document.getElementById('noComments');

      // Обновление счетчика комментариев
      function updateCommentsCount() {
        const count = commentsList.children.length;
        commentsCount.textContent = count + ' ' + getCommentWord(count);
        
        if (count === 0) {
          noComments.style.display = 'block';
          commentsList.style.display = 'none';
        } else {
          noComments.style.display = 'none';
          commentsList.style.display = 'flex';
        }
      }

      // Получение правильной формы слова
      function getCommentWord(count) {
        if (count % 10 === 1 && count % 100 !== 11) return 'комментарий';
        if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return 'комментария';
        return 'комментариев';
      }

      // Добавление нового комментария
      submitCommentBtn.addEventListener('click', () => {
        const text = commentText.value.trim();
        const rating = commentRating.value;
        
        if (text === '') {
          alert('Пожалуйста, напишите комментарий');
          return;
        }

        // Создание нового комментария
        const newComment = document.createElement('div');
        newComment.className = 'comment-card';
        newComment.innerHTML = `
          <div class="comment-header">
            <div class="comment-user">
              <div class="user-avatar">В</div>
              <div class="user-info">
                <div class="user-name">Вы</div>
                <div class="comment-date">только что</div>
              </div>
            </div>
            <div class="comment-rating">
              <i class="fas fa-star"></i>
              <span>${rating}.0</span>
            </div>
          </div>
          <div class="comment-content">${text}</div>
          <div class="comment-actions">
            <button class="comment-action">
              <i class="far fa-thumbs-up"></i>
              <span>0</span>
            </button>
            <button class="comment-action">
              <i class="far fa-thumbs-down"></i>
              <span>0</span>
            </button>
            <button class="comment-action">
              <i class="far fa-flag"></i>
            </button>
          </div>
        `;

        // Добавление комментария в начало списка
        commentsList.insertBefore(newComment, commentsList.firstChild);
        
        // Очистка формы
        commentText.value = '';
        commentRating.value = '5';
        
        // Обновление счетчика
        updateCommentsCount();
        
        // Прокрутка к новому комментарию
        newComment.scrollIntoView({ behavior: 'smooth' });
      });

      // Лайки и дизлайки для комментариев
      document.addEventListener('click', (e) => {
        if (e.target.closest('.comment-action')) {
          const action = e.target.closest('.comment-action');
          const countSpan = action.querySelector('span');
          
          if (countSpan) {
            let count = parseInt(countSpan.textContent);
            countSpan.textContent = count + 1;
          }
        }
      });

        updateCommentsCount();
})