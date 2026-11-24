"""Фабрика приложения Витте-Дашборд (Flask)."""
from flask import Flask, g, request

from app import auth, db
from app.config import Config
from app.helpers import page

# Пункты главного меню: (название, endpoint, нужен ли вход)
MAIN_MENU = [
    ("Главная", "public.index"),
    ("О модуле", "public.about"),
    ("Возможности", "public.features"),
    ("Показатели", "public.indicators"),
    ("Факультеты", "public.faculties"),
    ("Направления", "public.directions"),
    ("Открытая статистика", "public.open_stats"),
    ("Новости", "public.news_list"),
    ("Вопросы и ответы", "public.faq"),
    ("Документация", "public.docs"),
    ("Контакты", "public.contacts"),
]


def create_app(config_object=Config) -> Flask:
    """Создаёт и настраивает экземпляр приложения."""
    app = Flask(__name__)
    app.config.from_object(config_object)
    # Каталоги для файлов создаются при старте, если их ещё нет
    app.config["UPLOAD_DIR"].mkdir(parents=True, exist_ok=True)
    app.config["EXPORT_DIR"].mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    app.before_request(auth.load_user)
    app.before_request(auth.check_csrf)

    # Blueprint-ы импортируются здесь, чтобы избежать циклических импортов
    from app.blueprints import admin, api, auth_views, cabinet, dashboards, ops, public, reports

    for module in (public, auth_views, dashboards, api, reports, cabinet, admin, ops):
        app.register_blueprint(module.bp)

    @app.after_request
    def add_security_headers(response):
        """Защитные заголовки: запрет подмены типа файла, встраивания в чужие страницы и т.п."""
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

    @app.context_processor
    def inject_globals():
        """Переменные, доступные во всех шаблонах."""
        return {
            "main_menu": MAIN_MENU,
            "csrf_token": auth.csrf_token,
            "author_name": app.config["AUTHOR_NAME"],
            "thesis_topic": app.config["THESIS_TOPIC"],
            "current_user": g.get("user"),
            "active_endpoint": request.endpoint or "",
        }

    @app.template_filter("dt")
    def format_datetime(value):
        """Формат даты и времени ДД.ММ.ГГГГ ЧЧ:ММ."""
        return value.strftime("%d.%m.%Y %H:%M") if value else "—"

    @app.template_filter("num")
    def format_number(value):
        """Число с пробелом как разделителем тысяч и без лишних нулей."""
        number = float(value)
        text = f"{number:,.2f}".replace(",", " ")
        return text[:-3] if text.endswith(".00") else text

    for code, title, text in (
        (400, "Некорректный запрос", "Запрос не прошёл проверку (например, истёк токен формы)."),
        (403, "Доступ запрещён", "У вашей роли недостаточно прав для просмотра этой страницы."),
        (404, "Страница не найдена", "Такой страницы не существует или она была удалена."),
        (413, "Файл слишком большой", "Максимальный размер загружаемого файла — 5 МБ."),
        (500, "Внутренняя ошибка", "На сервере произошла ошибка. Попробуйте повторить действие позже."),
    ):
        def handler(_error, code=code, title=title, text=text):
            return page("error.html", crumbs=[(title, None)], code=code, title=title, text=text), code

        app.register_error_handler(code, handler)

    return app
