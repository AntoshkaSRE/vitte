"""Личный кабинет пользователя."""
import json

from flask import Blueprint, abort, current_app, flash, g, redirect, request, send_file, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import audit, login_required
from app.db import execute, query_all, query_one
from app.helpers import page, to_int
from app.passwords import check_strength
from app.services import files, stats

bp = Blueprint("cabinet", __name__, url_prefix="/cabinet")

# Допустимые значения личных настроек
CHART_TYPES = {"bar": "Столбчатая", "line": "Линейная", "pie": "Круговая"}
THEMES = {"light": "Светлая", "dark": "Тёмная"}
EMAIL_OK = lambda value: "@" in value and "." in value.split("@")[-1]  # noqa: E731


@bp.route("/")
@login_required
def index():
    """Обзор кабинета: сводка активности пользователя."""
    uid = g.user["id"]
    summary = query_one(
        """SELECT (SELECT COUNT(*) FROM report_history WHERE user_id = %s) AS reports,
                  (SELECT COUNT(*) FROM uploaded_files WHERE user_id = %s) AS files,
                  (SELECT COUNT(*) FROM audit_log WHERE user_id = %s) AS actions""", (uid, uid, uid))
    last = query_all("SELECT action, details, created_at FROM audit_log WHERE user_id = %s "
                     "ORDER BY created_at DESC LIMIT 5", (uid,))
    return page("cabinet/index.html", crumbs=[("Личный кабинет", None)], summary=summary, last=last)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Редактирование ФИО и электронной почты."""
    errors = []
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        if len(full_name) < 5:
            errors.append("Укажите ФИО полностью.")
        if email and not EMAIL_OK(email):
            errors.append("Адрес электронной почты указан некорректно.")
        if not errors:
            execute("UPDATE users SET full_name = %s, email = %s WHERE id = %s",
                    (full_name[:120], email[:120], g.user["id"]))
            audit("profile", "Изменены данные профиля")
            flash("Профиль сохранён.", "success")
            return redirect(url_for("cabinet.profile"))
    return page("cabinet/profile.html",
                crumbs=[("Личный кабинет", url_for("cabinet.index")), ("Профиль", None)], errors=errors)


@bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Смена пароля с проверкой текущего."""
    errors = []
    if request.method == "POST":
        old, new, again = (request.form.get(k, "") for k in ("old", "new", "again"))
        row = query_one("SELECT password_hash FROM users WHERE id = %s", (g.user["id"],))
        if not check_password_hash(row["password_hash"], old):
            errors.append("Текущий пароль указан неверно.")
        weakness = check_strength(new, g.user["login"])
        if weakness:
            errors.append(f"Новый пароль: {weakness}")
        if new != again:
            errors.append("Подтверждение не совпадает с новым паролем.")
        if not errors:
            execute("UPDATE users SET password_hash = %s WHERE id = %s",
                    (generate_password_hash(new, method="pbkdf2:sha256"), g.user["id"]))
            audit("password", "Пароль изменён")
            flash("Пароль успешно изменён.", "success")
            return redirect(url_for("cabinet.index"))
    return page("cabinet/password.html",
                crumbs=[("Личный кабинет", url_for("cabinet.index")), ("Смена пароля", None)], errors=errors)


@bp.route("/reports")
@login_required
def reports():
    """История сформированных пользователем отчётов."""
    rows = query_all("SELECT * FROM report_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 50",
                     (g.user["id"],))
    return page("cabinet/reports.html",
                crumbs=[("Личный кабинет", url_for("cabinet.index")), ("Мои отчёты", None)], rows=rows)


@bp.route("/reports/<int:report_id>/download")
@login_required
def report_download(report_id):
    """Повторная загрузка ранее созданного отчёта (только своего)."""
    row = query_one("SELECT * FROM report_history WHERE id = %s AND user_id = %s", (report_id, g.user["id"]))
    path = current_app.config["EXPORT_DIR"] / row["file_name"] if row else None
    if row is None or not path.exists():
        abort(404)
    return send_file(path, as_attachment=True, download_name=row["file_name"])


@bp.route("/files", methods=["GET", "POST"])
@login_required
def my_files():
    """Личные файлы пользователя: загрузка, список, скачивание, удаление."""
    if request.method == "POST":
        upload = request.files.get("file")
        if upload is None or not upload.filename:
            flash("Выберите файл для загрузки.", "danger")
        else:
            try:
                saved = files.save_upload(g.user["id"], upload)
                audit("upload", f"Загружен файл {saved['original_name']}")
                flash(f"Файл «{saved['original_name']}» загружен.", "success")
            except ValueError as exc:
                flash(str(exc), "danger")
        return redirect(url_for("cabinet.my_files"))
    return page("cabinet/files.html",
                crumbs=[("Личный кабинет", url_for("cabinet.index")), ("Мои файлы", None)],
                rows=files.list_files(g.user["id"]),
                extensions=sorted(current_app.config["ALLOWED_EXTENSIONS"]))


@bp.route("/files/<int:file_id>/download")
@login_required
def file_download(file_id):
    """Скачивание личного файла."""
    found = files.get_file(g.user["id"], file_id)
    if found is None or not found[1].exists():
        abort(404)
    return send_file(found[1], as_attachment=True, download_name=found[0]["original_name"])


@bp.route("/files/<int:file_id>/delete", methods=["POST"])
@login_required
def file_delete(file_id):
    """Удаление личного файла."""
    if files.delete_file(g.user["id"], file_id):
        audit("delete_file", f"Удалён файл #{file_id}")
        flash("Файл удалён.", "info")
    else:
        abort(404)
    return redirect(url_for("cabinet.my_files"))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Личные настройки: период по умолчанию, тип графика, тема оформления."""
    if request.method == "POST":
        prefs = {
            "period": to_int(request.form.get("period")),
            "chart": request.form.get("chart") if request.form.get("chart") in CHART_TYPES else "bar",
            "theme": request.form.get("theme") if request.form.get("theme") in THEMES else "light",
        }
        execute("UPDATE users SET preferences = %s::jsonb WHERE id = %s", (json.dumps(prefs), g.user["id"]))
        audit("settings", "Изменены личные настройки")
        flash("Настройки сохранены.", "success")
        return redirect(url_for("cabinet.settings"))
    return page("cabinet/settings.html",
                crumbs=[("Личный кабинет", url_for("cabinet.index")), ("Настройки", None)],
                periods=stats.list_periods(), chart_types=CHART_TYPES, themes=THEMES)
