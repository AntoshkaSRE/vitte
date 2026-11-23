"""Публичные страницы, доступные без авторизации."""
import re

from flask import Blueprint, abort, flash, redirect, request, url_for

from app.db import execute, query_all, query_one
from app.helpers import page, to_int
from app.services import stats

bp = Blueprint("public", __name__)

# Вопросы и ответы для страницы FAQ
FAQ_ITEMS = [
    ("Для чего нужен модуль Витте-Дашборд?",
     "Он автоматически строит дашборды и отчёты по данным единого центра статистики "
     "и избавляет сотрудников от ручной выгрузки данных из 1С в Excel."),
    ("Откуда берутся данные?",
     "Данные загружаются из HTTP-сервиса «1С:Предприятие» и сохраняются в витрину PostgreSQL. "
     "Актуальность кэша — не более одного часа, обновить данные можно кнопкой «Обновить»."),
    ("Как получить учётную запись?",
     "Учётные записи создаёт администратор системы. Заявку можно отправить через форму обратной связи."),
    ("Какие роли предусмотрены?",
     "Администратор, Руководство, УМУ и Деканат. Деканат видит только данные своего факультета."),
    ("В каких форматах можно выгрузить отчёт?",
     "XLSX, DOCX и CSV. Диаграммы дашбордов можно сохранить в формате PNG, а страницу — распечатать в PDF."),
    ("Какие браузеры поддерживаются?",
     "Яндекс.Браузер, Google Chrome, Mozilla Firefox и Microsoft Edge последних версий."),
    ("Можно ли пользоваться системой со смартфона?",
     "Да, интерфейс адаптивен и корректно отображается на экранах телефонов и планшетов."),
]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.route("/")
def index():
    """Главная страница: ключевые цифры и последние новости."""
    period_id = stats.latest_period_id()
    totals = {}
    for code in ("STUDENTS_TOTAL", "AVG_GRADE", "STAFF_TOTAL"):
        ind = stats.indicator_by_code(code)
        totals[code] = stats.kpi_total(ind["id"], period_id) if ind and period_id else 0
    counts = query_one(
        """SELECT (SELECT COUNT(*) FROM faculties) AS faculties,
                  (SELECT COUNT(*) FROM directions) AS directions,
                  (SELECT COUNT(*) FROM study_groups) AS groups""")
    news = query_all("""SELECT id, title, summary, published_at FROM news
                         WHERE is_published ORDER BY published_at DESC LIMIT 3""")
    period = query_one("SELECT title FROM academic_periods WHERE id = %s", (period_id,))
    return page("public/index.html", totals=totals, counts=counts, news=news,
                period_title=period["title"] if period else "—")


@bp.route("/about")
def about():
    """О модуле: цели, назначение и архитектура."""
    return page("public/about.html", crumbs=[("О модуле", None)])


@bp.route("/features")
def features():
    """Описание возможностей модуля."""
    return page("public/features.html", crumbs=[("Возможности", None)])


@bp.route("/indicators")
def indicators():
    """Каталог статистических показателей."""
    category = request.args.get("category", "")
    rows = query_all(
        """SELECT * FROM indicators WHERE (%s = '' OR category = %s) ORDER BY category, id""",
        (category, category))
    categories = query_all("SELECT DISTINCT category FROM indicators ORDER BY category")
    return page("public/indicators.html", crumbs=[("Показатели", None)], indicators=rows,
                categories=categories, selected=category)


@bp.route("/faculties")
def faculties():
    """Список факультетов с числом направлений и кафедр."""
    rows = query_all(
        """SELECT f.*, (SELECT COUNT(*) FROM directions d WHERE d.faculty_id = f.id) AS directions,
                  (SELECT COUNT(*) FROM departments c WHERE c.faculty_id = f.id) AS departments
             FROM faculties f ORDER BY f.id""")
    return page("public/faculties.html", crumbs=[("Факультеты", None)], faculties=rows)


@bp.route("/faculties/<code>")
def faculty_detail(code):
    """Карточка факультета: направления, кафедры, открытые показатели."""
    faculty = query_one("SELECT * FROM faculties WHERE code = %s", (code.upper(),))
    if faculty is None:
        abort(404)
    directions = query_all("SELECT * FROM directions WHERE faculty_id = %s ORDER BY code", (faculty["id"],))
    departments = query_all("SELECT * FROM departments WHERE faculty_id = %s ORDER BY name", (faculty["id"],))
    period_id = stats.latest_period_id()
    public_values = query_all(
        """SELECT i.name, i.unit, v.value FROM indicator_values v
             JOIN indicators i ON i.id = v.indicator_id
            WHERE v.faculty_id = %s AND v.period_id = %s AND i.is_public ORDER BY i.id""",
        (faculty["id"], period_id))
    return page("public/faculty.html",
                crumbs=[("Факультеты", url_for("public.faculties")), (faculty["short_name"], None)],
                faculty=faculty, directions=directions, departments=departments, values=public_values)


@bp.route("/directions")
def directions():
    """Направления подготовки с поиском по названию или коду."""
    q = request.args.get("q", "").strip()
    rows = query_all(
        """SELECT d.*, f.short_name AS faculty,
                  (SELECT COUNT(*) FROM study_groups g WHERE g.direction_id = d.id) AS groups
             FROM directions d JOIN faculties f ON f.id = d.faculty_id
            WHERE d.name ILIKE %s OR d.code ILIKE %s ORDER BY d.code""",
        (f"%{q}%", f"%{q}%"))
    return page("public/directions.html", crumbs=[("Направления", None)], directions=rows, q=q)


@bp.route("/open-stats")
def open_stats():
    """Открытая статистика: диаграммы по публичным показателям без авторизации."""
    public = query_all("SELECT id, code, name, unit FROM indicators WHERE is_public ORDER BY id")
    return page("public/open_stats.html", crumbs=[("Открытая статистика", None)],
                indicators=public, periods=stats.list_periods(), latest=stats.latest_period_id())


@bp.route("/news")
def news_list():
    """Лента новостей с постраничной навигацией."""
    per_page = 4
    current = max(to_int(request.args.get("page"), 1), 1)
    total = query_one("SELECT COUNT(*) AS n FROM news WHERE is_published")["n"]
    rows = query_all(
        """SELECT id, title, summary, published_at FROM news WHERE is_published
            ORDER BY published_at DESC LIMIT %s OFFSET %s""", (per_page, (current - 1) * per_page))
    pages = max((total + per_page - 1) // per_page, 1)
    return page("public/news_list.html", crumbs=[("Новости", None)], news=rows,
                current=current, pages=pages)


@bp.route("/news/<int:news_id>")
def news_detail(news_id):
    """Страница отдельной новости."""
    item = query_one(
        """SELECT n.*, u.full_name AS author FROM news n LEFT JOIN users u ON u.id = n.author_id
            WHERE n.id = %s AND n.is_published""", (news_id,))
    if item is None:
        abort(404)
    return page("public/news_detail.html",
                crumbs=[("Новости", url_for("public.news_list")), (item["title"], None)], item=item)


@bp.route("/faq")
def faq():
    """Вопросы и ответы."""
    return page("public/faq.html", crumbs=[("Вопросы и ответы", None)], items=FAQ_ITEMS)


@bp.route("/docs")
def docs():
    """Документация: краткое руководство пользователя и справка по системе."""
    return page("public/docs.html", crumbs=[("Документация", None)])


@bp.route("/contacts", methods=["GET", "POST"])
def contacts():
    """Контакты и форма обратной связи."""
    form = {"name": "", "email": "", "subject": "", "message": ""}
    errors = []
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in form}
        if len(form["name"]) < 2:
            errors.append("Укажите имя (не короче двух символов).")
        if not EMAIL_RE.match(form["email"]):
            errors.append("Введите корректный адрес электронной почты.")
        if len(form["subject"]) < 3:
            errors.append("Укажите тему обращения.")
        if len(form["message"]) < 10:
            errors.append("Сообщение должно содержать не менее 10 символов.")
        if not errors:
            execute("""INSERT INTO feedback_messages (name, email, subject, message)
                       VALUES (%s, %s, %s, %s)""",
                    (form["name"][:120], form["email"][:120], form["subject"][:160], form["message"]))
            flash("Спасибо! Ваше обращение отправлено.", "success")
            return redirect(url_for("public.contacts"))
    return page("public/contacts.html", crumbs=[("Контакты", None)], form=form, errors=errors)


@bp.route("/sitemap")
def sitemap():
    """Карта сайта."""
    return page("public/sitemap.html", crumbs=[("Карта сайта", None)])
