// Построение диаграмм Chart.js для дашбордов и открытой статистики

const PALETTE = ["#2f5d94", "#e8a33d", "#1f8a5b", "#c0392b", "#7d5ba6", "#2aa7b8", "#8a6d3b", "#d6568c"];

// Хранилище созданных диаграмм: нужно, чтобы корректно пересоздавать их при смене фильтров
const charts = {};

/** Возвращает конфигурацию Chart.js для виджета в зависимости от его типа. */
function buildConfig(widget) {
  const isCircle = widget.type === "pie" || widget.type === "doughnut";
  const dataset = {
    label: widget.unit ? `${widget.title}, ${widget.unit}` : widget.title,
    data: widget.values,
    backgroundColor: isCircle ? PALETTE : PALETTE[0],
    borderColor: widget.type === "line" ? PALETTE[0] : "#fff",
    borderWidth: widget.type === "line" ? 3 : 1,
    tension: 0.3,
    fill: false,
  };
  return {
    type: widget.type === "line" ? "line" : widget.type,
    data: { labels: widget.labels, datasets: [dataset] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: isCircle, position: "bottom" } },
      scales: isCircle ? {} : { y: { beginAtZero: widget.type !== "line" } },
    },
  };
}

/** Отрисовывает или обновляет один виджет внутри элемента #widget-<id>. */
function renderWidget(widget) {
  const root = document.getElementById(`widget-${widget.id}`);
  if (!root) return;
  const body = root.querySelector(".chart-box");
  if (widget.type === "kpi") {
    const value = widget.values[0] ?? 0;
    body.innerHTML = `<div class="kpi-value">${Number(value).toLocaleString("ru-RU")}</div>
      <p class="muted" style="text-align:center">${widget.unit || ""}</p>`;
    return;
  }
  if (!widget.labels.length) {
    body.innerHTML = '<p class="muted">Нет данных за выбранный период.</p>';
    return;
  }
  // Если ранее выводилось сообщение, возвращаем холст
  if (!body.querySelector("canvas")) body.innerHTML = "<canvas></canvas>";
  if (charts[widget.id]) charts[widget.id].destroy();
  charts[widget.id] = new Chart(body.querySelector("canvas"), buildConfig(widget));
}

/** Загружает данные дашборда с сервера и перерисовывает все виджеты.
 *  prefChart — предпочтительный тип графика из личных настроек: заменяет столбчатые диаграммы. */
async function loadDashboard(url, prefChart) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    document.querySelectorAll(".chart-box").forEach((box) => {
      box.innerHTML = '<p class="muted">Не удалось загрузить данные.</p>';
    });
    return;
  }
  (await response.json()).forEach((widget) => {
    if (widget.type === "bar" && (prefChart === "line" || prefChart === "pie")) widget.type = prefChart;
    renderWidget(widget);
  });
}

/** Сохраняет диаграмму виджета в PNG-файл. */
function exportPng(widgetId, title) {
  const chart = charts[widgetId];
  if (!chart) return;
  const link = document.createElement("a");
  link.href = chart.toBase64Image("image/png", 1);
  link.download = `${title}.png`;
  link.click();
}

/** Строит пару диаграмм открытой статистики для выбранного показателя. */
async function loadPublic(code, period) {
  const response = await fetch(`/api/public/${code}?period=${period}`);
  if (!response.ok) return;
  const data = await response.json();
  const unit = data.indicator.unit;
  renderWidget({ id: "pub-compare", type: "bar", title: data.indicator.name, unit, ...data.compare });
  renderWidget({ id: "pub-dynamics", type: "line", title: data.indicator.name, unit, ...data.dynamics });
}
