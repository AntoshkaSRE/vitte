"""Работа с файловой системой: загрузка, хранение и удаление файлов пользователей."""
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from app.db import execute, query_all, query_one


def allowed(filename: str) -> bool:
    """Проверяет расширение файла по белому списку из конфигурации."""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def user_dir(user_id: int) -> Path:
    """Возвращает (и при необходимости создаёт) личный каталог пользователя."""
    path = Path(current_app.config["UPLOAD_DIR"]) / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(user_id: int, storage) -> dict:
    """Сохраняет загруженный файл на диск под случайным именем и регистрирует его в БД.

    Оригинальное имя хранится только в базе — это исключает подмену пути.
    """
    original = storage.filename or ""
    if not original or not allowed(original):
        raise ValueError("Недопустимый тип файла")
    extension = original.rsplit(".", 1)[1].lower()
    stored = f"{uuid.uuid4().hex}.{extension}"
    target = user_dir(user_id) / stored
    storage.save(target)
    size = target.stat().st_size
    return execute(
        """INSERT INTO uploaded_files (user_id, original_name, stored_name, size_bytes)
           VALUES (%s, %s, %s, %s) RETURNING id, original_name""",
        (user_id, secure_filename(original) or f"file.{extension}", stored, size),
        returning=True)


def list_files(user_id: int) -> list[dict]:
    """Файлы пользователя, новые сверху."""
    return query_all(
        "SELECT * FROM uploaded_files WHERE user_id = %s ORDER BY uploaded_at DESC", (user_id,))


def get_file(user_id: int, file_id: int) -> tuple[dict, Path] | None:
    """Возвращает запись и путь к файлу, только если он принадлежит пользователю."""
    row = query_one("SELECT * FROM uploaded_files WHERE id = %s AND user_id = %s", (file_id, user_id))
    if row is None:
        return None
    return row, user_dir(user_id) / row["stored_name"]


def delete_file(user_id: int, file_id: int) -> bool:
    """Удаляет файл с диска и запись из базы."""
    found = get_file(user_id, file_id)
    if found is None:
        return False
    row, path = found
    path.unlink(missing_ok=True)
    execute("DELETE FROM uploaded_files WHERE id = %s", (row["id"],))
    return True
