"""Кэш агрегатов в таблице cache_entries (требование ТЗ: данные не старше 1 часа)."""
import json

from flask import current_app

from app.db import execute, query_one


def get_cached(key: str, compute):
    """Возвращает значение из кэша либо вычисляет его функцией compute() и сохраняет.

    Запись считается актуальной, пока её возраст меньше CACHE_TTL секунд.
    """
    ttl = current_app.config["CACHE_TTL"]
    row = query_one(
        """SELECT payload FROM cache_entries
            WHERE cache_key = %s AND created_at > NOW() - make_interval(secs => %s)""",
        (key, ttl),
    )
    if row is not None:
        return row["payload"]
    value = compute()
    execute(
        """INSERT INTO cache_entries (cache_key, payload, created_at) VALUES (%s, %s::jsonb, NOW())
           ON CONFLICT (cache_key) DO UPDATE SET payload = EXCLUDED.payload, created_at = NOW()""",
        (key, json.dumps(value, default=float, ensure_ascii=False)),
    )
    return value


def clear_cache() -> int:
    """Полностью очищает кэш (после синхронизации с 1С или по кнопке «Обновить»)."""
    row = execute("WITH d AS (DELETE FROM cache_entries RETURNING 1) SELECT COUNT(*) AS n FROM d",
                  returning=True)
    return row["n"]
