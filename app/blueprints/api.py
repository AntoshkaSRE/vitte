"""JSON-API для построения диаграмм на клиенте (Chart.js)."""
from flask import Blueprint, abort, jsonify, request

from app.auth import login_required
from app.blueprints.dashboards import load_dashboard, resolve_filters
from app.db import query_all, query_one
from app.helpers import to_int
from app.services import stats

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/dashboard/<code>")
@login_required
def dashboard_data(code):
    """Данные всех виджетов дашборда с учётом выбранных фильтров."""
    dash = load_dashboard(code)
    period_id, faculty_id = resolve_filters()
    widgets = query_all(
        """SELECT w.id, w.title, w.chart_type, w.indicator_id, i.unit
             FROM dashboard_widgets w JOIN indicators i ON i.id = w.indicator_id
            WHERE w.dashboard_id = %s ORDER BY w.position""", (dash["id"],))
    return jsonify([stats.widget_data(w, period_id, faculty_id) for w in widgets])


@bp.route("/public/<code>")
def public_data(code):
    """Открытые данные по публичному показателю: сравнение по факультетам и динамика."""
    ind = query_one("SELECT * FROM indicators WHERE code = %s AND is_public", (code.upper(),))
    if ind is None:
        abort(404)
    period_id = to_int(request.args.get("period"), None) or stats.latest_period_id()
    return jsonify({
        "indicator": {"code": ind["code"], "name": ind["name"], "unit": ind["unit"]},
        "compare": stats.compare_by_faculty(ind["id"], period_id),
        "dynamics": stats.dynamics(ind["id"]),
    })
