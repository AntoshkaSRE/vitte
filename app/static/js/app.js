// Общие скрипты интерфейса Витте-Дашборд

document.addEventListener("DOMContentLoaded", () => {
  // Кнопка-«гамбургер»: раскрывает главное меню на узких экранах
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  if (toggle && menu) {
    toggle.addEventListener("click", () => {
      const open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Подтверждение опасных действий (удаление): форма с атрибутом data-confirm
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) {
        event.preventDefault();
      }
    });
  });

  // Автоматическая отправка фильтров при смене значения списка
  document.querySelectorAll("select[data-autosubmit]").forEach((select) => {
    select.addEventListener("change", () => select.form.submit());
  });
});
