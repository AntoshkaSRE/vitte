"""Тесты аутентификации и разграничения прав доступа."""
import pytest

from tests.conftest import USERS, login, post

PRIVATE_URLS = ["/dashboards/", "/reports/", "/cabinet/", "/cabinet/profile", "/cabinet/files",
                "/admin/", "/admin/users", "/api/dashboard/kpi"]


@pytest.mark.parametrize("url", PRIVATE_URLS)
def test_private_pages_redirect_anonymous(client, url):
    """Неавторизованный пользователь перенаправляется на страницу входа."""
    response = client.get(url)
    assert response.status_code == 302 and "/login" in response.headers["Location"]


@pytest.mark.parametrize("name", list(USERS))
def test_login_all_users(client, name):
    response = login(client, name)
    assert response.status_code == 302
    assert client.get("/cabinet/").status_code == 200


def test_login_wrong_password(client):
    response = post(client, "/login", {"login": "admin", "password": "wrong"})
    assert "Неверный логин или пароль" in response.get_data(as_text=True)


def test_login_unknown_user(client):
    response = post(client, "/login", {"login": "ghost", "password": "x"})
    assert response.status_code == 200 and "Неверный логин" in response.get_data(as_text=True)


def test_sql_injection_in_login(client):
    """Безопасность: SQL-инъекция в поле логина не даёт войти."""
    response = post(client, "/login", {"login": "admin' OR '1'='1", "password": "x"})
    assert response.status_code == 200
    assert client.get("/cabinet/").status_code == 302


def test_open_redirect_blocked(client):
    response = post(client, "/login?next=//evil.example.com", {"login": "admin", "password": USERS["admin"]})
    assert "evil.example.com" not in response.headers["Location"]


def test_logout(as_admin):
    post(as_admin, "/logout")
    assert as_admin.get("/cabinet/").status_code == 302


def test_logout_requires_post(as_admin):
    assert as_admin.get("/logout").status_code == 405


@pytest.mark.parametrize("name", ["rector", "umu", "dean_fit"])
def test_admin_forbidden_for_other_roles(client, name):
    login(client, name)
    assert client.get("/admin/").status_code == 403
    assert client.get("/admin/users").status_code == 403


def test_dean_cannot_open_leadership_dashboard(as_dean):
    assert as_dean.get("/dashboards/kpi").status_code == 403
    assert as_dean.get("/api/dashboard/kpi").status_code == 403


def test_umu_cannot_open_leadership_dashboard(client):
    login(client, "umu")
    assert client.get("/dashboards/kpi").status_code == 403
    assert client.get("/dashboards/staff").status_code == 200


def test_rector_opens_all_dashboards(client):
    login(client, "rector")
    for code in ("kpi", "contingent", "performance", "staff", "science"):
        assert client.get(f"/dashboards/{code}").status_code == 200


def test_blocked_user_loses_access(client, fresh_db):
    login(client, "admin")
    login_client = client
    # Блокируем rector через панель администратора и проверяем, что его вход невозможен
    users = login_client.get("/admin/users").get_data(as_text=True)
    assert "rector" in users
    other = client.application.test_client()
    post(login_client, "/admin/users/2/edit", {"full_name": "Петров Владимир Николаевич", "role_id": 2,
                                                "email": "", "faculty_id": ""})
    response = post(other, "/login", {"login": "rector", "password": USERS["rector"]})
    assert "Неверный логин" in response.get_data(as_text=True)


def test_login_throttled_after_failures(client, fresh_db):
    """После пяти неудачных попыток вход блокируется даже с верным паролем."""
    for _ in range(5):
        response = post(client, "/login", {"login": "admin", "password": "wrong"})
        assert response.status_code == 200
    blocked = post(client, "/login", {"login": "admin", "password": USERS["admin"]})
    assert blocked.status_code == 429
    assert "Слишком много неудачных попыток" in blocked.get_data(as_text=True)
    assert client.get("/cabinet/").status_code == 302


def test_throttle_is_per_login(client, fresh_db):
    """Блокировка одной учётной записи не мешает входу другой."""
    for _ in range(5):
        post(client, "/login", {"login": "admin", "password": "wrong"})
    assert login(client, "rector").status_code == 302


def test_successful_login_resets_counter(client, fresh_db):
    """Успешный вход обнуляет счётчик неудач."""
    for _ in range(4):
        post(client, "/login", {"login": "umu", "password": "wrong"})
    assert login(client, "umu").status_code == 302
    post(client, "/logout")
    for _ in range(4):
        post(client, "/login", {"login": "umu", "password": "wrong"})
    assert login(client, "umu").status_code == 302