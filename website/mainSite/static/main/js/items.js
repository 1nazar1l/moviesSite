document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('resetFilters').addEventListener('click', function () {
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

    const sortSelect = document.getElementById('sortSelect');
    const moviesGrid = document.getElementById('moviesGrid');

    if (sortSelect && moviesGrid) {
        sortSelect.addEventListener('change', function () {
            const sortBy = this.value;
            sortItems(sortBy);
        });
    }

    function sortItems(sortBy) {
        const items = Array.from(moviesGrid.querySelectorAll('a'));

        if (items.length === 0) return;

        items.sort((a, b) => {
            let valueA, valueB;

            switch (sortBy) {
                case 'rating':
                    console.log("Pairs: ", a.dataset.rating, b.dataset.rating)
                    valueA = a.dataset.rating;
                    valueA = valueA.replace(",", ".");
                    valueB = b.dataset.rating;
                    valueB = valueB.replace(",", ".");
                    valueA = parseInt(parseFloat(valueA) * 100);
                    valueB = parseInt(parseFloat(valueB) * 100);
                    console.log("Pairs: ", valueA, valueA)
                    return valueB - valueA; // по убыванию

                case 'release_date':
                    valueA = new Date(a.dataset.date || 0).getTime();
                    valueB = new Date(b.dataset.date || 0).getTime();
                    return valueB - valueA; // по убыванию (новые первые)

                case 'title':
                    valueA = a.dataset.title || '';
                    valueB = b.dataset.title || '';
                    return valueA.localeCompare(valueB); // по алфавиту

                default:
                    return 0;
            }
        });

        // Очищаем контейнер и добавляем отсортированные элементы
        moviesGrid.innerHTML = '';
        items.forEach(item => moviesGrid.appendChild(item));
    }
})