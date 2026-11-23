"""Точка входа Витте-Дашборд: запуск веб-приложения командой `python main.py`.

Для размещения на хостинге используется WSGI-объект app
(например, `gunicorn main:app`).
"""
import os

from app import create_app

# WSGI-приложение, которое подхватывают gunicorn и другие серверы
app = create_app()

if __name__ == "__main__":
    # Локальный запуск для разработки и демонстрации
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("FLASK_DEBUG") == "1")
