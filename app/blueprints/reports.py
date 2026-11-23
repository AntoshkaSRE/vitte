"""Формирование отчётов в форматах XLSX, DOCX, CSV."""
import json
from datetime import datetime

from flask import Blueprint, abort, flash, g, redirect, request, send_file, url_for
from flask import current_app

from app.auth import audit, faculty_scope, login_required
from app.db import execute
from app.helpers import page, to_int
from app.services import exporter, stats

bp = Blueprint("reports", __name__, url_prefix="/reports")

MIME = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "csv": "text/csv; charset=utf-8",
}


@bp.route("/")
@login_required
def index():
    """Форма выбора типа отчёта, периода, факультета и формата."""
    return page("reports/index.html", crumbs=[("Отчёты", None)], types=exporter.REPORT_TYPES,
                periods=stats.list_periods(), faculties=stats.list_faculties(),
                locked=faculty_scope() is not None, latest=stats.latest_period_id())


@bp.route("/generate", methods=["POST"])
@login_required
def generate():
    """Формирует файл отчёта, сохраняет копию на диск и запись в историю."""
    report_type = request.form.get("report_type", "")
    file_format = request.form.get("format", "")
    period_id = to_int(request.form.get("period"))
    faculty_id = faculty_scope() or to_int(request.form.get("faculty"))
    if report_type not in exporter.REPORT_TYPES or file_format not in MIME or not period_id:
        flash("Выберите корректные параметры отчёта.", "danger")
        return redirect(url_for("reports.index"))
    period = next((p for p in stats.list_periods() if p["id"] == period_id), None)
    if period is None:
        abort(404)
    headers, rows = exporter.build_table(report_type, period_id, faculty_id)
    title = f'{exporter.REPORT_TYPES[report_type]} — {period["title"]}'
    if file_format == "xlsx":
        content = exporter.to_xlsx(title, headers, rows)
    elif file_format == "docx":
        content = exporter.to_docx(title, headers, rows, g.user["full_name"])
    else:
        content = exporter.to_csv(headers, rows)
    file_name = f"{report_type}_{datetime.now():%Y%m%d_%H%M%S}_{g.user['id']}.{file_format}"
    (current_app.config["EXPORT_DIR"] / file_name).write_bytes(content)
    execute("""INSERT INTO report_history (user_id, report_type, params, file_format, file_name)
               VALUES (%s, %s, %s::jsonb, %s, %s)""",
            (g.user["id"], report_type, json.dumps({"period": period_id, "faculty": faculty_id or "all"}),
             file_format, file_name))
    audit("report", f"Отчёт {report_type} ({file_format})")
    return send_file(current_app.config["EXPORT_DIR"] / file_name, mimetype=MIME[file_format],
                     as_attachment=True, download_name=file_name)
