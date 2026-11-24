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
