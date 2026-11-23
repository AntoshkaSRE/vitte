"""Аутентификация, ролевая модель доступа, CSRF-защита и журнал аудита."""
import secrets
from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for

from app.db import execute, query_one

# Уровни ролей: чем выше число, тем шире права (совпадает с roles.level)
ROLE_ADMIN = 4
ROLE_LEADERSHIP = 3
ROLE_UMU = 2
ROLE_DEAN = 1


def load_user() -> None:
    """Загружает пользователя из сессии в g.user (вызывается перед каждым запросом)."""
    g.user = None
    user_id = session.get("user_id")
    if user_id:
        g.user = query_one(
            """SELECT u.id, u.login, u.full_name, u.email, u.faculty_id, u.preferences,
                      u.is_active, r.code AS role_code, r.name AS role_name, r.level AS role_level,
                      f.short_name AS faculty_name
                 FROM users u JOIN roles r ON r.id = u.role_id
                 LEFT JOIN faculties f ON f.id = u.faculty_id
                WHERE u.id = %s""",
            (user_id,),
        )
        # Заблокированного или удалённого пользователя немедленно разлогиниваем
        if g.user is None or not g.user["is_active"]:
            session.clear()
            g.user = None


def login_required(view):
    """Декоратор: страница доступна только вошедшим пользователям."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Для доступа к разделу необходимо войти в систему.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def role_required(min_level: int):
    """Декоратор: доступ только ролям с уровнем не ниже min_level."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user["role_level"] < min_level:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def audit(action: str, details: str = "") -> None:
    """Записывает действие пользователя в журнал аудита."""
    user_id = g.user["id"] if getattr(g, "user", None) else None
    execute(
        "INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (%s, %s, %s, %s)",
        (user_id, action, details[:500], request.remote_addr or ""),
    )


def csrf_token() -> str:
    """Возвращает CSRF-токен сессии, создавая его при первом обращении."""
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def check_csrf() -> None:
    """Проверяет CSRF-токен у всех POST-запросов (подключается к before_request)."""
    if request.method == "POST":
        sent = request.form.get("csrf_token", "")
        if not sent or not secrets.compare_digest(sent, session.get("csrf", "")):
            abort(400, "Недействительный CSRF-токен")


def faculty_scope() -> int | None:
    """Возвращает id факультета, которым ограничен пользователь (для деканата), иначе None."""
    if g.user and g.user["role_level"] <= ROLE_DEAN:
        return g.user["faculty_id"]
    return None
