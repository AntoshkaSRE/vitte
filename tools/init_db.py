"""Инициализация базы данных: создание БД (если нет), схемы и тестовых данных.

Запуск: python tools/init_db.py [--test]
  --test  — работать с тестовой базой (vitte_test), используемой автотестами.
"""
import sys
from pathlib import Path

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo

# Позволяет запускать скрипт из корня проекта без установки пакета
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import BASE_DIR, Config, TestConfig  # noqa: E402
from app.db import run_sql_file  # noqa: E402


def ensure_database(url: str) -> None:
    """Создаёт базу данных из строки подключения, если она ещё не существует."""
    params = conninfo_to_dict(url)
    name = params.pop("dbname")
    with psycopg.connect(make_conninfo(**params, dbname="postgres"), autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone()
        if not exists:
            conn.execute(f'CREATE DATABASE "{name}" ENCODING \'UTF8\' TEMPLATE template0')
            print(f"База данных {name} создана")


def main() -> None:
    """Применяет схему и загружает тестовые данные."""
    url = (TestConfig if "--test" in sys.argv else Config).DATABASE_URL
    ensure_database(url)
    run_sql_file(BASE_DIR / "sql" / "create_tables.sql", url)
    run_sql_file(BASE_DIR / "sql" / "insert_test_data.sql", url)
    print("Схема создана, тестовые данные загружены")


if __name__ == "__main__":
    main()
