document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('resetFilters').addEventListener('click', function() {
      // Очищаем все поля формы
      const form = document.getElementById('filterForm');
      const inputs = form.querySelectorAll('input, select');
      
      inputs.forEach(input => {
          if (input.type === 'text' || input.type === 'date') {
              input.value = '';
          } else if (input.tagName === 'SELECT') {
              input.selectedIndex = -1;
          }
      });
      
      // Отправляем форму
      form.submit();
  });
})