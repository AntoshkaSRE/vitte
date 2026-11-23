"""Дашборды для авторизованных пользователей."""
from flask import Blueprint, abort, flash, g, redirect, request, url_for

from app.auth import audit, faculty_scope, login_required
from app.db import query_all, query_one
from app.helpers import page, to_int
from app.services import stats
from app.services.cache import clear_cache

bp = Blueprint("dashboards", __name__, url_prefix="/dashboards")


def available_dashboards() -> list[dict]:
    """Дашборды, доступные роли текущего пользователя."""
    return query_all("""SELECT d.*, (SELECT COUNT(*) FROM dashboard_widgets w WHERE w.dashboard_id = d.id) AS widgets
                          FROM dashboards d WHERE d.min_role_level <= %s ORDER BY d.min_role_level DESC, d.id""",
                     (g.user["role_level"],))


def load_dashboard(code: str) -> dict:
    """Загружает дашборд, проверяя право доступа (иначе 404/403)."""
    dash = query_one("SELECT * FROM dashboards WHERE code = %s", (code,))
    if dash is None:
        abort(404)
    if dash["min_role_level"] > g.user["role_level"]:
        abort(403)
    return dash


def resolve_filters() -> tuple[int, int | None]:
    """Определяет период и факультет из параметров запроса с учётом прав деканата."""
    period_id = to_int(request.args.get("period"), None) or stats.latest_period_id()
    faculty_id = faculty_scope() or to_int(request.args.get("faculty"), None)
    return period_id, faculty_id


@bp.route("/")
@login_required
def index():
    """Список дашбордов, доступных пользователю."""
    return page("dashboards/index.html", crumbs=[("Дашборды", None)], dashboards=available_dashboards())


@bp.route("/<code>")
@login_required
def show(code):
    """Страница дашборда с фильтрами по периоду и факультету."""
    dash = load_dashboard(code)
    period_id, faculty_id = resolve_filters()
    widgets = query_all("SELECT id, title, chart_type FROM dashboard_widgets WHERE dashboard_id = %s ORDER BY position",
                        (dash["id"],))
    audit("dashboard", f"Просмотр дашборда {code}")
    return page("dashboards/show.html",
                crumbs=[("Дашборды", url_for("dashboards.index")), (dash["title"], None)],
                dash=dash, widgets=widgets, periods=stats.list_periods(),
                faculties=stats.list_faculties(), period_id=period_id, faculty_id=faculty_id,
                locked=faculty_scope() is not None)


@bp.route("/refresh", methods=["POST"])
@login_required
def refresh():
    """Кнопка «Обновить»: сбрасывает кэш агрегатов, данные пересчитываются при следующем запросе."""
    removed = clear_cache()
    audit("refresh", f"Сброс кэша, удалено записей: {removed}")
    flash("Данные дашбордов обновлены.", "success")
    return redirect(request.form.get("back") or url_for("dashboards.index"))
