"""Панель администратора (доступна только роли «Администратор»)."""
import psycopg
from flask import Blueprint, abort, flash, g, redirect, request, url_for
from werkzeug.security import generate_password_hash

from app.auth import ROLE_ADMIN, audit, role_required
from app.db import execute, query_all, query_one
from app.helpers import page, to_int
from app.passwords import check_strength
from app.services import onec
from app.services.cache import clear_cache

bp = Blueprint("admin", __name__, url_prefix="/admin")
CRUMB_ROOT = ("Администрирование", "/admin/")


@bp.route("/")
@role_required(ROLE_ADMIN)
def index():
    """Сводка: количество записей, последняя синхронизация, свежие события."""
    counts = query_one(
        """SELECT (SELECT COUNT(*) FROM users) AS users,
                  (SELECT COUNT(*) FROM users WHERE is_active) AS active_users,
                  (SELECT COUNT(*) FROM feedback_messages WHERE NOT is_processed) AS new_feedback,
                  (SELECT COUNT(*) FROM cache_entries) AS cache,
                  (SELECT COUNT(*) FROM report_history) AS reports""")
    last_sync = query_one("SELECT * FROM sync_log ORDER BY started_at DESC LIMIT 1")
    events = query_all("""SELECT a.*, u.login FROM audit_log a LEFT JOIN users u ON u.id = a.user_id
                           ORDER BY a.created_at DESC LIMIT 8""")
    return page("admin/index.html", crumbs=[("Администрирование", None)], counts=counts,
                last_sync=last_sync, events=events)


# ------------------------------ пользователи ------------------------------
@bp.route("/users")
@role_required(ROLE_ADMIN)
def users():
    """Список пользователей."""
    rows = query_all("""SELECT u.*, r.name AS role_name, f.short_name AS faculty
                          FROM users u JOIN roles r ON r.id = u.role_id
                          LEFT JOIN faculties f ON f.id = u.faculty_id ORDER BY u.id""")
    return page("admin/users.html", crumbs=[CRUMB_ROOT, ("Пользователи", None)], rows=rows)


def user_form_data():
    """Справочники для формы пользователя."""
    return {"roles": query_all("SELECT * FROM roles ORDER BY level DESC"),
            "faculties": query_all("SELECT id, short_name FROM faculties ORDER BY id")}


@bp.route("/users/new", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def user_new():
    """Создание пользователя."""
    errors, form = [], {}
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in ("login", "full_name", "email", "role_id", "faculty_id")}
        password = request.form.get("password", "")
        if len(form["login"]) < 3 or not form["login"].replace("_", "").isalnum():
            errors.append("Логин: от 3 символов, латиница, цифры и «_».")
        if len(form["full_name"]) < 5:
            errors.append("Укажите ФИО полностью.")
        weakness = check_strength(password, form["login"])
        if weakness:
            errors.append(weakness)
        if not to_int(form["role_id"]):
            errors.append("Выберите роль.")
        if not errors:
            try:
                execute("""INSERT INTO users (login, password_hash, full_name, email, role_id, faculty_id)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (form["login"], generate_password_hash(password, method="pbkdf2:sha256"),
                         form["full_name"], form["email"], int(form["role_id"]), to_int(form["faculty_id"])))
                audit("user_create", f"Создан пользователь {form['login']}")
                flash("Пользователь создан.", "success")
                return redirect(url_for("admin.users"))
            except psycopg.errors.UniqueViolation:
                g.db.rollback()
                errors.append("Пользователь с таким логином уже существует.")
    return page("admin/user_form.html", crumbs=[CRUMB_ROOT, ("Пользователи", url_for("admin.users")), ("Новый", None)],
                errors=errors, form=form, edit=None, **user_form_data())


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def user_edit(user_id):
    """Редактирование пользователя: роль, факультет, блокировка, сброс пароля."""
    target = query_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if target is None:
        abort(404)
    errors = []
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        role_id = to_int(request.form.get("role_id"))
        active = request.form.get("is_active") == "on"
        password = request.form.get("password", "")
        if target["id"] == g.user["id"] and not active:
            errors.append("Нельзя заблокировать собственную учётную запись.")
        if target["id"] == g.user["id"] and role_id != target["role_id"]:
            errors.append("Нельзя изменить собственную роль: система должна сохранить администратора.")
        if len(full_name) < 5:
            errors.append("Укажите ФИО полностью.")
        weakness = check_strength(password, target["login"]) if password else None
        if weakness:
            errors.append(f"Новый пароль: {weakness}")
        if not errors:
            execute("""UPDATE users SET full_name = %s, email = %s, role_id = %s, faculty_id = %s, is_active = %s
                       WHERE id = %s""",
                    (full_name, request.form.get("email", "").strip(), role_id,
                     to_int(request.form.get("faculty_id")), active, user_id))
            if password:
                execute("UPDATE users SET password_hash = %s WHERE id = %s",
                        (generate_password_hash(password, method="pbkdf2:sha256"), user_id))
            audit("user_edit", f"Изменён пользователь {target['login']}")
            flash("Изменения сохранены.", "success")
            return redirect(url_for("admin.users"))
    return page("admin/user_form.html",
                crumbs=[CRUMB_ROOT, ("Пользователи", url_for("admin.users")), (target["login"], None)],
                errors=errors, form={}, edit=target, **user_form_data())


# ------------------------------- справочники ------------------------------
@bp.route("/catalogs", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def catalogs():
    """Справочник факультетов: просмотр, добавление, удаление."""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            code = request.form.get("code", "").strip().upper()
            name = request.form.get("name", "").strip()
            short = request.form.get("short_name", "").strip()
            if code and name and short:
                try:
                    execute("INSERT INTO faculties (code, name, short_name) VALUES (%s, %s, %s)",
                            (code[:10], name[:160], short[:40]))
                    audit("faculty_add", f"Добавлен факультет {code}")
                    flash("Факультет добавлен.", "success")
                except psycopg.errors.UniqueViolation:
                    g.db.rollback()
                    flash("Факультет с таким кодом уже существует.", "danger")
            else:
                flash("Заполните все поля формы.", "danger")
        elif action == "delete":
            fid = to_int(request.form.get("id"))
            used = query_one("SELECT COUNT(*) AS n FROM indicator_values WHERE faculty_id = %s", (fid,))["n"]
            if used:
                flash("Нельзя удалить факультет, по которому есть статистические данные.", "danger")
            else:
                execute("DELETE FROM faculties WHERE id = %s", (fid,))
                audit("faculty_delete", f"Удалён факультет #{fid}")
                flash("Факультет удалён.", "info")
        return redirect(url_for("admin.catalogs"))
    rows = query_all("""SELECT f.*, (SELECT COUNT(*) FROM directions d WHERE d.faculty_id = f.id) AS directions
                          FROM faculties f ORDER BY f.id""")
    return page("admin/catalogs.html", crumbs=[CRUMB_ROOT, ("Справочник факультетов", None)], rows=rows)


@bp.route("/indicators", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def indicators():
    """Управление показателями: открытый доступ, добавление."""
    if request.method == "POST":
        if request.form.get("action") == "toggle":
            execute("UPDATE indicators SET is_public = NOT is_public WHERE id = %s",
                    (to_int(request.form.get("id")),))
            clear_cache()
            flash("Признак публичности изменён.", "success")
        elif request.form.get("action") == "add":
            code = request.form.get("code", "").strip().upper()
            name = request.form.get("name", "").strip()
            if code and name:
                try:
                    execute("""INSERT INTO indicators (code, name, unit, category) VALUES (%s, %s, %s, %s)""",
                            (code[:30], name[:160], request.form.get("unit", "чел.")[:20],
                             request.form.get("category", "Прочее")[:40]))
                    flash("Показатель добавлен.", "success")
                except psycopg.errors.UniqueViolation:
                    g.db.rollback()
                    flash("Показатель с таким кодом уже существует.", "danger")
        return redirect(url_for("admin.indicators"))
    rows = query_all("SELECT * FROM indicators ORDER BY id")
    return page("admin/indicators.html", crumbs=[CRUMB_ROOT, ("Показатели", None)], rows=rows)


# ----------------------------- новости и обращения ------------------------
@bp.route("/news", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def news():
    """Управление новостями: публикация, скрытие, удаление."""
    if request.method == "POST":
        action, nid = request.form.get("action"), to_int(request.form.get("id"))
        if action == "add":
            title = request.form.get("title", "").strip()
            body = request.form.get("body", "").strip()
            if title and body:
                execute("""INSERT INTO news (title, summary, body, author_id) VALUES (%s, %s, %s, %s)""",
                        (title[:200], body[:200], body, g.user["id"]))
                flash("Новость опубликована.", "success")
            else:
                flash("Заполните заголовок и текст новости.", "danger")
        elif action == "toggle":
            execute("UPDATE news SET is_published = NOT is_published WHERE id = %s", (nid,))
        elif action == "delete":
            execute("DELETE FROM news WHERE id = %s", (nid,))
            flash("Новость удалена.", "info")
        return redirect(url_for("admin.news"))
    rows = query_all("SELECT * FROM news ORDER BY published_at DESC")
    return page("admin/news.html", crumbs=[CRUMB_ROOT, ("Новости", None)], rows=rows)


@bp.route("/feedback", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def feedback():
    """Обращения из формы обратной связи."""
    if request.method == "POST":
        execute("UPDATE feedback_messages SET is_processed = TRUE WHERE id = %s", (to_int(request.form.get("id")),))
        return redirect(url_for("admin.feedback"))
    rows = query_all("SELECT * FROM feedback_messages ORDER BY is_processed, created_at DESC")
    return page("admin/feedback.html", crumbs=[CRUMB_ROOT, ("Обращения", None)], rows=rows)


# ------------------------------ интеграция и аудит ------------------------
@bp.route("/integration", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def integration():
    """Настройки подключения к 1С и запуск синхронизации."""
    if request.method == "POST":
        if request.form.get("action") == "save":
            for key in ("onec_url", "onec_login", "onec_base", "sync_interval_minutes"):
                onec.set_setting(key, request.form.get(key, "").strip())
            audit("integration", "Изменены настройки интеграции")
            flash("Настройки сохранены.", "success")
        else:
            result = onec.run_sync(g.user["id"])
            audit("sync", f"Синхронизация: {result['status']}")
            flash("Синхронизация завершена: загружено записей " + str(result["rows"])
                  if result["status"] == "ok" else "Ошибка синхронизации: " + result["message"],
                  "success" if result["status"] == "ok" else "danger")
        return redirect(url_for("admin.integration"))
    settings = {r["key"]: r["value"] for r in query_all("SELECT key, value FROM integration_settings")}
    log = query_all("SELECT * FROM sync_log ORDER BY started_at DESC LIMIT 15")
    return page("admin/integration.html", crumbs=[CRUMB_ROOT, ("Интеграция с 1С", None)],
                settings=settings, log=log)


@bp.route("/audit")
@role_required(ROLE_ADMIN)
def audit_log():
    """Журнал аудита с фильтром по действию."""
    action = request.args.get("action", "")
    rows = query_all("""SELECT a.*, u.login FROM audit_log a LEFT JOIN users u ON u.id = a.user_id
                         WHERE (%s = '' OR a.action = %s) ORDER BY a.created_at DESC LIMIT 200""",
                     (action, action))
    actions = query_all("SELECT DISTINCT action FROM audit_log ORDER BY action")
    return page("admin/audit.html", crumbs=[CRUMB_ROOT, ("Журнал аудита", None)], rows=rows,
                actions=actions, selected=action)
