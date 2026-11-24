"""Тесты служебных адресов и настроек безопасности (проверка работоспособности, заголовки и т.п.)."""
from app.blueprints import ops


def test_healthz_ok(client):
    """Проверка работоспособности отвечает 200 и сообщает о доступной базе данных."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


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