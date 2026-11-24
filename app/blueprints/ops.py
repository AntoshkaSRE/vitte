"""Служебные адреса: проверка работоспособности для хостинга и мониторинга."""
from flask import Blueprint, jsonify

from app.db import query_one

bp = Blueprint("ops", __name__)


@bp.route("/healthz")
def healthz():
    """Возвращает 200, если приложение запущено и доступна база данных, иначе 503."""
    try:
        query_one("SELECT 1 AS ok")
    except Exception:  # noqa: BLE001 - любая ошибка подключения означает «база недоступна»
        return jsonify(status="error", database="unavailable"), 503
    return jsonify(status="ok", database="ok")
