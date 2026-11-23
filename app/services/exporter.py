"""Формирование отчётов в форматах XLSX, DOCX и CSV."""
import csv
import io
from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# Типы отчётов: код -> название (используется на странице формирования отчёта)
REPORT_TYPES = {
    "performance": "Успеваемость по учебным группам",
    "summary": "Сводные показатели по факультетам",
}

HEADER_FILL = PatternFill("solid", fgColor="1F3A5F")


def build_table(report_type: str, period_id: int, faculty_id: int | None):
    """Собирает заголовки и строки таблицы выбранного отчёта."""
    from app.services import stats

    if report_type == "performance":
        rows = stats.groups_performance(period_id, faculty_id)
        headers = ["Факультет", "Код направления", "Направление", "Группа", "Курс",
                   "Форма", "Студентов", "Средний балл", "Сдали без долгов, %"]
        data = [[r["faculty"], r["direction_code"], r["direction"], r["group_name"], r["course"],
                 r["study_form"], r["students"], float(r["avg_grade"]), float(r["passed_percent"])]
                for r in rows]
    else:
        rows = stats.faculty_summary(period_id, faculty_id)
        headers = ["Факультет", "Категория", "Показатель", "Ед. изм.", "Значение"]
        data = [[r["faculty"], r["category"], r["indicator"], r["unit"], float(r["value"])]
                for r in rows]
    return headers, data


def to_xlsx(title: str, headers: list, rows: list) -> bytes:
    """Создаёт XLSX-книгу с оформленным заголовком и диаграммой по последнему столбцу."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчёт"
    ws.append([title])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append([f"Сформировано: {datetime.now():%d.%m.%Y %H:%M}"])
    ws.append([])
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=4, column=col)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    for row in rows:
        ws.append(row)
    # Автоподбор ширины столбцов по самому длинному значению
    for idx, header in enumerate(headers, start=1):
        longest = max([len(str(header))] + [len(str(r[idx - 1])) for r in rows[:200]])
        ws.column_dimensions[get_column_letter(idx)].width = min(longest + 2, 45)
    if rows:
        chart = BarChart()
        chart.title = headers[-1]
        values = Reference(ws, min_col=len(headers), min_row=4, max_row=min(4 + len(rows), 24))
        # Подписи оси: «Группа» (4-й столбец) в отчёте успеваемости, «Показатель» (3-й) в сводном
        cat_col = 4 if len(headers) == 9 else 3
        cats = Reference(ws, min_col=cat_col, min_row=5, max_row=min(4 + len(rows), 24))
        chart.add_data(values, titles_from_data=True)
        chart.set_categories(cats)
        chart.height, chart.width = 8, 18
        ws.add_chart(chart, f"{get_column_letter(len(headers) + 2)}4")
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def to_docx(title: str, headers: list, rows: list, author: str) -> bytes:
    """Создаёт DOCX-документ с заголовком и таблицей данных."""
    doc = Document()
    heading = doc.add_heading(title, level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Сформировано: {datetime.now():%d.%m.%Y %H:%M}. Исполнитель: {author}.")
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    for idx, header in enumerate(headers):
        table.rows[0].cells[idx].text = str(header)
    for row in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = str(value)
    doc.add_paragraph("Источник данных: единый центр статистических данных (модуль Витте-Дашборд).")
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def to_csv(headers: list, rows: list) -> bytes:
    """Создаёт CSV (кодировка UTF-8 с BOM, разделитель «;» — для открытия в Excel)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(headers)
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")
