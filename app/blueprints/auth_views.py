"""Вход и выход из системы."""
from flask import Blueprint, flash, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash

from app.auth import audit
from app.db import execute, query_one
from app.helpers import page

bp = Blueprint("auth", __name__)


def safe_next(target: str | None) -> str:
    """Допускает только внутренние адреса для перенаправления после входа."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("cabinet.index")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Форма входа: проверка логина и пароля."""
    if g.user:
        return redirect(url_for("cabinet.index"))
    error = None
    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        user = query_one("SELECT * FROM users WHERE login = %s", (login_value,))
        if user and user["is_active"] and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user["id"],))
            g.user = {"id": user["id"]}
            audit("login", "Вход в систему")
            return redirect(safe_next(request.args.get("next")))
        error = "Неверный логин или пароль, либо учётная запись заблокирована."
    return page("auth/login.html", crumbs=[("Вход", None)], error=error)


@bp.route("/logout", methods=["POST"])
def logout():
    """Выход из системы (только POST, чтобы исключить выход по ссылке)."""
    if g.user:
        audit("logout", "Выход из системы")
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("public.index"))
