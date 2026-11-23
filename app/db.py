"""Слой доступа к PostgreSQL.

Используется прямой SQL через psycopg 3: так запросы остаются прозрачными
и их легко описать в отчёте. Соединение открывается один раз на HTTP-запрос
и закрывается автоматически по его завершении.
"""
from pathlib import Path

import psycopg
from flask import current_app, g
from psycopg.rows import dict_row


def get_db() -> psycopg.Connection:
    """Возвращает соединение, привязанное к текущему запросу."""
    if "db" not in g:
        g.db = psycopg.connect(current_app.config["DATABASE_URL"], row_factory=dict_row)
    return g.db


def close_db(_exc=None) -> None:
    """Закрывает соединение в конце запроса (подключается к teardown)."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql: str, params=None) -> list[dict]:
    """Выполняет SELECT и возвращает список словарей."""
    with get_db().cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


def query_one(sql: str, params=None) -> dict | None:
    """Выполняет SELECT и возвращает первую строку или None."""
    with get_db().cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


def execute(sql: str, params=None, returning: bool = False):
    """Выполняет INSERT/UPDATE/DELETE и фиксирует транзакцию.

    Если указан returning=True, возвращает первую строку результата
    (удобно для получения id созданной записи).
    """
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        row = cur.fetchone() if returning else None
    db.commit()
    return row


def run_sql_file(path: Path, database_url: str) -> None:
    """Выполняет SQL-скрипт целиком (создание схемы и загрузка тестовых данных)."""
    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute(Path(path).read_text(encoding="utf-8"))


def init_app(app) -> None:
    """Регистрирует закрытие соединения в приложении Flask."""
    app.teardown_appcontext(close_db)
