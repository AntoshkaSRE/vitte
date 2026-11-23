"""Тесты публичной части: страницы, «хлебные крошки», форма обратной связи."""
import pytest

from tests.conftest import post

PUBLIC_URLS = [
    "/", "/about", "/features", "/indicators", "/faculties", "/faculties/FIT",
    "/directions", "/open-stats", "/news", "/news/1", "/faq", "/docs", "/contacts",
    "/sitemap", "/login",
]


@pytest.mark.parametrize("url", PUBLIC_URLS)
def test_public_pages_open(client, url):
    """Смоук-тест: каждая публичная страница отвечает 200 и содержит ФИО автора в подвале."""
    response = client.get(url)
    assert response.status_code == 200
    assert "Новоселов Антон Андреевич" in response.get_data(as_text=True)


@pytest.mark.parametrize("url", PUBLIC_URLS)
def test_breadcrumbs_on_every_page(client, url):
    """На каждой странице присутствуют «хлебные крошки»."""
    assert 'class="breadcrumbs"' in client.get(url).get_data(as_text=True)


def test_unknown_page_returns_404(client):
    assert client.get("/no-such-page").status_code == 404


def test_unknown_faculty_returns_404(client):
    assert client.get("/faculties/XXX").status_code == 404


def test_directions_search(client):
    html = client.get("/directions?q=09.03.03").get_data(as_text=True)
    assert "Прикладная информатика" in html
    assert "Юриспруденция" not in html


def test_indicators_filter_by_category(client):
    html = client.get("/indicators?category=Кадры").get_data(as_text=True)
    assert "STAFF_TOTAL" in html and "STUDENTS_TOTAL" not in html


def test_open_api_only_public_indicators(client):
    assert client.get("/api/public/STUDENTS_TOTAL").status_code == 200
    # Показатель EXPELLED не публичный — доступа без входа быть не должно
    assert client.get("/api/public/EXPELLED").status_code == 404


def test_feedback_valid(client, fresh_db):
    response = post(client, "/contacts", {
        "name": "Тестов Тест", "email": "t@example.com",
        "subject": "Проверка", "message": "Это тестовое обращение пользователя."},
        follow_redirects=True)
    assert "Ваше обращение отправлено" in response.get_data(as_text=True)


@pytest.mark.parametrize("field,value", [("email", "не-почта"), ("name", "А"), ("message", "коротко")])
def test_feedback_negative(client, field, value):
    """Негативное тестирование: некорректные данные формы отклоняются."""
    data = {"name": "Тестов Тест", "email": "t@example.com", "subject": "Тема", "message": "Достаточно длинный текст."}
    data[field] = value
    html = post(client, "/contacts", data).get_data(as_text=True)
    assert 'class="errors"' in html


def test_post_without_csrf_rejected(client):
    assert client.post("/contacts", data={"name": "x"}).status_code == 400
