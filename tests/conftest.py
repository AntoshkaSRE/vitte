"""Общие фикстуры автотестов: тестовая БД, клиент, вход под ролями."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app.config import BASE_DIR, TestConfig  # noqa: E402
from app.db import run_sql_file  # noqa: E402
from tools.init_db import ensure_database  # noqa: E402

# Учётные данные тестовых пользователей (совпадают с sql/insert_test_data.sql)
USERS = {
    "admin": "Admin#2026",
    "rector": "Rector#2026",
    "umu": "Umu#2026",
    "dean_fit": "Dean#2026",
    "dean_feu": "Dean#2026",
}


def reset_database() -> None:
    """Пересоздаёт схему и загружает тестовые данные в тестовую БД."""
    run_sql_file(BASE_DIR / "sql" / "create_tables.sql", TestConfig.DATABASE_URL)
    run_sql_file(BASE_DIR / "sql" / "insert_test_data.sql", TestConfig.DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def _database():
    """Один раз за сессию готовит тестовую базу данных."""
    ensure_database(TestConfig.DATABASE_URL)
    reset_database()


@pytest.fixture()
def fresh_db():
    """Возвращает базу к исходному состоянию (для тестов, изменяющих данные)."""
    reset_database()


@pytest.fixture()
def app(tmp_path):
    """Экземпляр приложения с временными каталогами файлов."""

    class Cfg(TestConfig):
        UPLOAD_DIR = tmp_path / "uploads"
        EXPORT_DIR = tmp_path / "exports"

    return create_app(Cfg)


@pytest.fixture()
def client(app):
    """Тестовый HTTP-клиент."""
    return app.test_client()


def csrf(client) -> str:
    """Возвращает CSRF-токен текущей сессии клиента."""
    with client.session_transaction() as sess:
        sess.setdefault("csrf", "test-token-123")
        return sess["csrf"]


def post(client, url, data=None, **kwargs):
    """POST-запрос с автоматической подстановкой CSRF-токена."""
    payload = dict(data or {})
    payload["csrf_token"] = csrf(client)
    return client.post(url, data=payload, **kwargs)


def login(client, name):
    """Выполняет вход под указанным пользователем."""
    return post(client, "/login", {"login": name, "password": USERS[name]})


@pytest.fixture()
def as_admin(client):
    login(client, "admin")
    return client


@pytest.fixture()
def as_dean(client):
    login(client, "dean_fit")
    return client
