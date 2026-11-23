"""Выборки статистических данных для дашбордов, API и отчётов."""
from app.db import query_all, query_one
from app.services.cache import get_cached


def list_periods() -> list[dict]:
    """Все учебные периоды от старых к новым."""
    return query_all("SELECT id, title, academic_year, semester FROM academic_periods ORDER BY start_date")


def list_faculties() -> list[dict]:
    """Все факультеты."""
    return query_all("SELECT id, code, name, short_name FROM faculties ORDER BY id")


def latest_period_id() -> int:
    """Идентификатор самого свежего периода, по которому есть данные."""
    row = query_one(
        """SELECT p.id FROM academic_periods p
            WHERE EXISTS (SELECT 1 FROM indicator_values v WHERE v.period_id = p.id)
            ORDER BY p.start_date DESC LIMIT 1""")
    return row["id"] if row else 0


def indicator_by_code(code: str) -> dict | None:
    """Описание показателя по его коду."""
    return query_one("SELECT * FROM indicators WHERE code = %s", (code,))


def compare_by_faculty(indicator_id: int, period_id: int, faculty_id: int | None = None) -> dict:
    """Значения показателя по факультетам за один период (для столбчатых и круговых диаграмм)."""

    def compute():
        rows = query_all(
            """SELECT f.short_name AS label, v.value
                 FROM indicator_values v JOIN faculties f ON f.id = v.faculty_id
                WHERE v.indicator_id = %s AND v.period_id = %s
                  AND (%s::int IS NULL OR f.id = %s::int)
                ORDER BY f.id""",
            (indicator_id, period_id, faculty_id, faculty_id))
        return {"labels": [r["label"] for r in rows], "values": [float(r["value"]) for r in rows]}

    return get_cached(f"cmp:{indicator_id}:{period_id}:{faculty_id}", compute)


def dynamics(indicator_id: int, faculty_id: int | None = None) -> dict:
    """Динамика показателя по периодам; без факультета — сумма (или среднее) по университету."""

    def compute():
        unit = query_one("SELECT unit FROM indicators WHERE id = %s", (indicator_id,))["unit"]
        # Для относительных величин (%, баллы) берём среднее, для абсолютных — сумму
        agg = "AVG" if unit in ("%", "балл") else "SUM"
        rows = query_all(
            f"""SELECT p.title AS label, ROUND({agg}(v.value), 2) AS value
                  FROM indicator_values v JOIN academic_periods p ON p.id = v.period_id
                 WHERE v.indicator_id = %s AND (%s::int IS NULL OR v.faculty_id = %s::int)
                 GROUP BY p.id, p.title, p.start_date ORDER BY p.start_date""",
            (indicator_id, faculty_id, faculty_id))
        return {"labels": [r["label"] for r in rows], "values": [float(r["value"]) for r in rows]}

    return get_cached(f"dyn:{indicator_id}:{faculty_id}", compute)


def kpi_total(indicator_id: int, period_id: int, faculty_id: int | None = None) -> float:
    """Итоговое значение показателя по университету (или факультету) за период."""
    data = compare_by_faculty(indicator_id, period_id, faculty_id)
    if not data["values"]:
        return 0.0
    unit = query_one("SELECT unit FROM indicators WHERE id = %s", (indicator_id,))["unit"]
    if unit in ("%", "балл"):
        return round(sum(data["values"]) / len(data["values"]), 2)
    return round(sum(data["values"]), 2)


def widget_data(widget: dict, period_id: int, faculty_id: int | None) -> dict:
    """Готовит данные одного виджета в зависимости от типа графика."""
    ind = widget["indicator_id"]
    if widget["chart_type"] == "line":
        data = dynamics(ind, faculty_id)
    elif widget["chart_type"] == "kpi":
        data = {"labels": [], "values": [kpi_total(ind, period_id, faculty_id)]}
    else:
        data = compare_by_faculty(ind, period_id, faculty_id)
    return {"id": widget["id"], "title": widget["title"], "type": widget["chart_type"],
            "unit": widget["unit"], **data}


def groups_performance(period_id: int, faculty_id: int | None = None) -> list[dict]:
    """Успеваемость по учебным группам (детальная таблица отчёта)."""
    return query_all(
        """SELECT f.short_name AS faculty, d.code AS direction_code, d.name AS direction,
                  g.name AS group_name, g.course, g.study_form, gp.students,
                  gp.avg_grade, gp.passed_percent
             FROM group_performance gp
             JOIN study_groups g ON g.id = gp.group_id
             JOIN directions d ON d.id = g.direction_id
             JOIN faculties f ON f.id = d.faculty_id
            WHERE gp.period_id = %s AND (%s::int IS NULL OR f.id = %s::int)
            ORDER BY f.id, d.code, g.course""",
        (period_id, faculty_id, faculty_id))


def faculty_summary(period_id: int, faculty_id: int | None = None) -> list[dict]:
    """Сводная таблица всех показателей по факультетам (отчёт «Сводный»)."""
    return query_all(
        """SELECT f.short_name AS faculty, i.category, i.name AS indicator, i.unit, v.value
             FROM indicator_values v
             JOIN indicators i ON i.id = v.indicator_id
             JOIN faculties f ON f.id = v.faculty_id
            WHERE v.period_id = %s AND (%s::int IS NULL OR f.id = %s::int)
            ORDER BY i.id, f.id""",
        (period_id, faculty_id, faculty_id))
