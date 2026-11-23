"""Интеграция с «1С:Предприятие» (подсистема ETL).

Источник данных — HTTP-сервис 1С, возвращающий JSON. Если адрес сервиса
не задан (ONEC_URL пуст), используется файл-эмулятор data/onec_export.json
с тем же форматом ответа. Загруженные значения сохраняются в витрину
indicator_values, после чего сбрасывается кэш агрегатов.
"""
import json
import urllib.error
import urllib.request

from flask import current_app

from app.db import execute, get_db, query_all, query_one
from app.services.cache import clear_cache


class SyncError(Exception):
    """Ошибка получения или разбора данных 1С."""


def get_setting(key: str, default: str = "") -> str:
    """Читает параметр интеграции из таблицы integration_settings."""
    row = query_one("SELECT value FROM integration_settings WHERE key = %s", (key,))
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    """Сохраняет параметр интеграции (создаёт или обновляет запись)."""
    execute(
        """INSERT INTO integration_settings (key, value, updated_at) VALUES (%s, %s, NOW())
           ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()""",
        (key, value))


def fetch_payload() -> tuple[dict, str]:
    """Получает JSON-выгрузку: по HTTP из 1С либо из файла-эмулятора.

    Возвращает пару (данные, источник).
    """
    url = get_setting("onec_url") or current_app.config["ONEC_URL"]
    if url:
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8")), "onec-http"
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise SyncError(f"Сервис 1С недоступен: {exc}") from exc
    path = current_app.config["ONEC_MOCK_FILE"]
    if not path.exists():
        raise SyncError("Файл-эмулятор выгрузки 1С не найден")
    return json.loads(path.read_text(encoding="utf-8")), "onec-file"


def validate_payload(payload: dict) -> list[dict]:
    """Проверяет структуру выгрузки и возвращает список записей значений."""
    values = payload.get("values")
    if not isinstance(values, list) or not values:
        raise SyncError("В выгрузке нет массива values")
    for item in values:
        if not {"indicator", "period", "faculty", "value"} <= set(item):
            raise SyncError(f"Некорректная запись выгрузки: {item}")
        if not isinstance(item["value"], (int, float)):
            raise SyncError(f"Значение не является числом: {item}")
    return values


def run_sync(started_by: int | None) -> dict:
    """Выполняет полную синхронизацию и пишет результат в sync_log."""
    log = execute(
        "INSERT INTO sync_log (source, started_by) VALUES ('pending', %s) RETURNING id",
        (started_by,), returning=True)
    try:
        payload, source = fetch_payload()
        values = validate_payload(payload)
        # Справочники для преобразования кодов 1С во внутренние идентификаторы
        indicators = {r["code"]: r["id"] for r in query_all("SELECT id, code FROM indicators")}
        faculties = {r["code"]: r["id"] for r in query_all("SELECT id, code FROM faculties")}
        periods = {f'{r["academic_year"]}-{r["semester"]}': r["id"]
                   for r in query_all("SELECT id, academic_year, semester FROM academic_periods")}
        loaded = 0
        db = get_db()
        with db.cursor() as cur:
            for item in values:
                ind = indicators.get(item["indicator"])
                fac = faculties.get(item["faculty"])
                per = periods.get(item["period"])
                if None in (ind, fac, per):
                    continue  # неизвестные коды пропускаем, но не прерываем загрузку
                cur.execute(
                    """INSERT INTO indicator_values (indicator_id, period_id, faculty_id, value)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (indicator_id, period_id, faculty_id)
                       DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()""",
                    (ind, per, fac, item["value"]))
                loaded += 1
        db.commit()
        clear_cache()
        execute("""UPDATE sync_log SET finished_at = NOW(), source = %s, status = 'ok',
                          rows_loaded = %s, message = %s WHERE id = %s""",
                (source, loaded, f"Загружено записей: {loaded} из {len(values)}", log["id"]))
        return {"status": "ok", "rows": loaded, "source": source}
    except SyncError as exc:
        get_db().rollback()
        execute("""UPDATE sync_log SET finished_at = NOW(), source = 'error', status = 'error',
                          message = %s WHERE id = %s""", (str(exc), log["id"]))
        return {"status": "error", "message": str(exc)}
