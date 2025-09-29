document.addEventListener('DOMContentLoaded', () => {

  const filterForm = document.getElementById("filterForm");
  const resetFiltersBtn = document.getElementById("resetFilters");

  filterForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const formData = new FormData(filterForm);
    const filters = {};

    for (let [key, value] of formData.entries()) {
      if (value) filters[key] = value;
    }

    console.log("Применены фильтры:", filters);
    alert(
      "Фильтры применены! (в реальном приложении здесь будет загрузка данных)"
    );
  });

  resetFiltersBtn.addEventListener("click", () => {
    filterForm.reset();
    console.log("Фильтры сброшены");
  });

  // Обработка сортировки
  const sortSelect = document.getElementById("sortSelect");

  sortSelect.addEventListener("change", () => {
    console.log("Сортировка изменена на:", sortSelect.value);
    // В реальном приложении здесь будет перезагрузка данных с новой сортировкой
  });

  // Обработка пагинации
  document.querySelectorAll(".page-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      document
        .querySelectorAll(".page-btn")
        .forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      console.log("Переход на страницу:", this.textContent);
      // В реальном приложении здесь будет загрузка данных для выбранной страницы
    });
  });
})