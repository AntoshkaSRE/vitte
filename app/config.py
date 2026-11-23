"""Конфигурация приложения Витте-Дашборд.

Все параметры читаются из переменных окружения (или из файла .env),
поэтому один и тот же код можно запускать локально, в тестах и на хостинге.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Корень проекта: на уровень выше пакета app
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env, если он есть (в продуктивной среде переменные задаёт хостинг)
load_dotenv(BASE_DIR / ".env")


class Config:
    """Базовые настройки, общие для всех режимов запуска."""

    # Строка подключения к PostgreSQL
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/vitte"
    )
    # Ключ подписи cookie-сессий
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    # Адрес HTTP-сервиса 1С (пусто — используется файл-эмулятор выгрузки)
    ONEC_URL = os.environ.get("ONEC_URL", "")
    # Время жизни кэша агрегатов в секундах (по ТЗ не более часа)
    CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))
    # Каталоги для загруженных файлов и выгруженных отчётов
    UPLOAD_DIR = BASE_DIR / "instance" / "uploads"
    EXPORT_DIR = BASE_DIR / "instance" / "exports"
    # Файл, имитирующий ответ HTTP-сервиса 1С
    ONEC_MOCK_FILE = BASE_DIR / "data" / "onec_export.json"
    # Ограничение размера загружаемого файла: 5 МБ
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    # Допустимые расширения загружаемых файлов
    ALLOWED_EXTENSIONS = {"xlsx", "docx", "csv", "pdf", "png", "jpg", "txt"}
    # Сведения об авторе, выводимые в подвале каждой страницы
    AUTHOR_NAME = "Новоселов Антон Андреевич"
    THESIS_TOPIC = (
        "Разработка модуля визуализации данных для единого центра "
        "статистических данных с интеграцией в 1С:Предприятие"
    )


class TestConfig(Config):
    """Настройки для автотестов: отдельная база и отключённый CSRF-контроль не требуются."""

    TESTING = True
    DATABASE_URL = os.environ.get(
        "TEST_DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/vitte_test"
    )
    CACHE_TTL = 3600
