"""Регрессионные тесты дефектов, найденных при исследовательском тестировании (см. docs/bug-reports.md)."""
from tests.conftest import login, post


def test_bug002_dean_without_faculty_sees_nothing(client, fresh_db):
    """BUG-002: деканат без привязки к факультету не должен видеть данные всех факультетов."""
    login(client, "admin")
    post(client, "/admin/users/new", {"login": "dean_none", "full_name": "Декан Безфакультетный",
                                       "email": "", "role_id": 4, "faculty_id": "", "password": "Strong#Pass1"})
    other = client.application.test_client()
    post(other, "/login", {"login": "dean_none", "password": "Strong#Pass1"})
    data = other.get("/api/dashboard/contingent").get_json()
    bar = next(w for w in data if w["type"] == "bar")
    assert bar["labels"] == [], "Пользователь без факультета увидел данные"


def test_bug003_admin_cannot_remove_own_admin_role(as_admin, fresh_db):
    """BUG-003: администратор не может сменить собственную роль (иначе система останется без администратора)."""
    html = post(as_admin, "/admin/users/1/edit", {"full_name": "Новоселов Антон Андреевич", "role_id": 3,
                                                   "is_active": "on"}).get_data(as_text=True)
    assert "собственную роль" in html
    assert as_admin.get("/admin/").status_code == 200


def test_bug004_refresh_open_redirect(client):
    """BUG-004: параметр back кнопки «Обновить» не должен допускать переход на внешний сайт."""
    login(client, "rector")
    response = post(client, "/dashboards/refresh", {"back": "https://evil.example.com/"})
    assert "evil.example.com" not in response.headers["Location"]


def test_bug005_default_period_from_settings_is_applied(client, fresh_db):
    """BUG-005: период по умолчанию из личных настроек должен применяться на дашбордах."""
    login(client, "rector")
    post(client, "/cabinet/settings", {"period": 1, "chart": "bar", "theme": "light"})
    html = client.get("/dashboards/contingent").get_data(as_text=True)
    assert 'value="1" selected' in html
