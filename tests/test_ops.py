"""Тесты служебных адресов и настроек безопасности (проверка работоспособности, заголовки и т.п.)."""
from app import __version__
from app.blueprints import ops


def test_healthz_ok(client):
    """Проверка работоспособности отвечает 200 и сообщает о доступной базе данных."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok", "version": __version__}


def test_healthz_database_down(client, monkeypatch):
    """При недоступной базе данных адрес возвращает 503, а не падает с исключением."""
    def broken(*_args, **_kwargs):
        raise RuntimeError("нет соединения")

    monkeypatch.setattr(ops, "query_one", broken)
    response = client.get("/healthz")
    assert response.status_code == 503
    assert response.get_json()["status"] == "error"


def test_robots_txt(client):
    """robots.txt закрывает личные разделы от индексации и указывает карту сайта."""
    response = client.get("/robots.txt")
    text = response.get_data(as_text=True)
    assert response.status_code == 200 and response.mimetype == "text/plain"
    assert "Disallow: /admin/" in text and "Disallow: /cabinet/" in text
    assert "Sitemap: http://localhost/sitemap.xml" in text


def test_sitemap_xml(client):
    """sitemap.xml содержит статические страницы, факультеты и новости."""
    response = client.get("/sitemap.xml")
    text = response.get_data(as_text=True)
    assert response.status_code == 200 and response.mimetype == "application/xml"
    assert "<loc>http://localhost/about</loc>" in text
    assert "<loc>http://localhost/faculties/FIT</loc>" in text
    assert "<loc>http://localhost/news/1</loc>" in text
    assert "/admin/" not in text

def test_security_headers(client):
    """Каждый ответ содержит защитные заголовки."""
    for url in ("/", "/login", "/healthz", "/no-such-page"):
        headers = client.get(url).headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "camera=()" in headers["Permissions-Policy"]

def test_session_cookie_flags(client):
    """Cookie сессии после входа имеет HttpOnly и SameSite=Lax, а срок жизни ограничен."""
    from tests.conftest import login
    response = login(client, "admin")
    cookie = response.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Expires=" in cookie

def test_favicon_linked_and_served(client):
    """Значок сайта подключён в шапке страницы и отдаётся по адресам /favicon.ico и /static/favicon.svg."""
    assert 'rel="icon"' in client.get("/").get_data(as_text=True)
    redirect = client.get("/favicon.ico")
    assert redirect.status_code == 301 and redirect.headers["Location"].endswith("/static/favicon.svg")
    svg = client.get("/static/favicon.svg")
    assert svg.status_code == 200 and svg.mimetype == "image/svg+xml"

def test_meta_description(client):
    """На каждой странице есть описание, а в новости оно берётся из краткого содержания."""
    assert 'name="description"' in client.get("/about").get_data(as_text=True)
    html = client.get("/news/1").get_data(as_text=True)
    assert 'name="description" content="' in html
    assert 'name="theme-color"' in html

def test_version_in_footer(client):
    """Номер версии выводится в подвале каждой страницы."""
    assert f"Версия {__version__}" in client.get("/").get_data(as_text=True)

def test_static_files_cached_and_versioned(client):
    """Статика кэшируется на неделю, а в разметке к её адресам добавлена версия (сброс кэша при обновлении)."""
    response = client.get("/static/css/style.css")
    assert "max-age=604800" in response.headers["Cache-Control"]
    html = client.get("/").get_data(as_text=True)
    assert f"style.css?v={__version__}" in html and f"app.js?v={__version__}" in html

def test_print_stylesheet_present(client):
    """В таблице стилей одно правило печати: навигация, формы и панели инструментов скрываются."""
    css = client.get("/static/css/style.css").get_data(as_text=True)
    assert css.count("@media print") == 1
    printed = css.split("@media print")[1]
    assert ".main-nav" in printed and "form" in printed and ".tools" in printed