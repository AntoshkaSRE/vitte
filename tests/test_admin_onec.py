"""Тесты панели администратора и интеграции с 1С."""
import json

import pytest

from app.db import query_one
from app.services import onec
from tests.conftest import post


def test_admin_pages_open(as_admin):
    for url in ("/admin/", "/admin/users", "/admin/users/new", "/admin/users/1/edit", "/admin/catalogs",
                "/admin/indicators", "/admin/news", "/admin/feedback", "/admin/integration", "/admin/audit"):
        assert as_admin.get(url).status_code == 200, url


def test_create_user_and_login(as_admin, fresh_db):
    response = post(as_admin, "/admin/users/new", {"login": "new_user", "full_name": "Новый Пользователь",
                                                    "email": "n@x.ru", "role_id": 3, "faculty_id": "", "password": "Strong#Pass1"})
    assert response.status_code == 302
    other = as_admin.application.test_client()
    assert post(other, "/login", {"login": "new_user", "password": "Strong#Pass1"}).status_code == 302


def test_create_duplicate_user(as_admin, fresh_db):
    data = {"login": "umu", "full_name": "Дубликат Тестович", "email": "", "role_id": 3, "faculty_id": "", "password": "Strong#Pass1"}
    html = post(as_admin, "/admin/users/new", data).get_data(as_text=True)
    assert "уже существует" in html


@pytest.mark.parametrize("field,value", [("login", "a"), ("password", "123"), ("full_name", "А")])
def test_create_user_validation(as_admin, field, value):
    data = {"login": "okuser", "full_name": "Нормальное Имя", "email": "", "role_id": 3, "faculty_id": "", "password": "Strong#Pass1"}
    data[field] = value
    assert 'class="errors"' in post(as_admin, "/admin/users/new", data).get_data(as_text=True)


def test_admin_cannot_block_himself(as_admin):
    html = post(as_admin, "/admin/users/1/edit", {"full_name": "Новоселов Антон Андреевич", "role_id": 1}).get_data(as_text=True)
    assert "Нельзя заблокировать собственную" in html


def test_edit_missing_user_404(as_admin):
    assert as_admin.get("/admin/users/9999/edit").status_code == 404


def test_add_and_delete_faculty(as_admin, fresh_db):
    post(as_admin, "/admin/catalogs", {"action": "add", "code": "tst", "name": "Тестовый факультет", "short_name": "ТФ"})
    assert "Тестовый факультет" in as_admin.get("/admin/catalogs").get_data(as_text=True)
    fid = query_one_in(as_admin, "SELECT id FROM faculties WHERE code = 'TST'")["id"]
    post(as_admin, "/admin/catalogs", {"action": "delete", "id": fid})
    assert "Тестовый факультет" not in as_admin.get("/admin/catalogs").get_data(as_text=True)


def test_cannot_delete_faculty_with_data(as_admin, fresh_db):
    html = post(as_admin, "/admin/catalogs", {"action": "delete", "id": 1}, follow_redirects=True).get_data(as_text=True)
    assert "Нельзя удалить факультет" in html


def test_toggle_indicator_public(as_admin, fresh_db):
    post(as_admin, "/admin/indicators", {"action": "toggle", "id": 5})
    assert as_admin.get("/api/public/EXPELLED").status_code == 200


def test_news_lifecycle(as_admin, fresh_db):
    post(as_admin, "/admin/news", {"action": "add", "title": "Тестовая новость", "body": "Текст тестовой новости."})
    assert "Тестовая новость" in as_admin.application.test_client().get("/news").get_data(as_text=True)


def test_feedback_mark_processed(as_admin, fresh_db):
    post(as_admin, "/admin/feedback", {"id": 1})
    assert "обработано" in as_admin.get("/admin/feedback").get_data(as_text=True)


def test_audit_logged_login(as_admin):
    assert "login" in as_admin.get("/admin/audit").get_data(as_text=True)


# ------------------------------- интеграция 1С ------------------------------
def query_one_in(client, sql):
    with client.application.app_context():
        return query_one(sql)


def test_sync_from_mock_file(as_admin, fresh_db):
    post(as_admin, "/admin/integration", {"action": "sync"})
    row = query_one_in(as_admin, "SELECT status, rows_loaded FROM sync_log ORDER BY id DESC LIMIT 1")
    assert row["status"] == "ok" and row["rows_loaded"] == 420


def test_sync_updates_value_and_resets_cache(app, tmp_path, fresh_db):
    payload = {"values": [{"indicator": "STUDENTS_TOTAL", "period": "2026/2027-1", "faculty": "FIT", "value": 1}]}
    mock = tmp_path / "onec.json"
    mock.write_text(json.dumps(payload), encoding="utf-8")
    app.config["ONEC_MOCK_FILE"] = mock
    with app.app_context():
        result = onec.run_sync(None)
        assert result == {"status": "ok", "rows": 1, "source": "onec-file"}
        value = query_one("SELECT v.value FROM indicator_values v JOIN indicators i ON i.id = v.indicator_id "
                          "JOIN faculties f ON f.id = v.faculty_id JOIN academic_periods p ON p.id = v.period_id "
                          "WHERE i.code='STUDENTS_TOTAL' AND f.code='FIT' AND p.academic_year='2026/2027'")
        assert float(value["value"]) == 1.0


@pytest.mark.parametrize("payload", [{}, {"values": []}, {"values": [{"indicator": "X"}]},
                                     {"values": [{"indicator": "A", "period": "p", "faculty": "F", "value": "текст"}]}])
def test_sync_rejects_bad_payload(app, tmp_path, payload, fresh_db):
    """Негативное тестирование: повреждённая выгрузка не загружается, ошибка попадает в журнал."""
    mock = tmp_path / "bad.json"
    mock.write_text(json.dumps(payload), encoding="utf-8")
    app.config["ONEC_MOCK_FILE"] = mock
    with app.app_context():
        result = onec.run_sync(None)
        assert result["status"] == "error"
        assert query_one("SELECT status FROM sync_log ORDER BY id DESC LIMIT 1")["status"] == "error"


def test_sync_missing_file(app, tmp_path, fresh_db):
    app.config["ONEC_MOCK_FILE"] = tmp_path / "none.json"
    with app.app_context():
        assert onec.run_sync(None)["status"] == "error"


def test_sync_unavailable_service(app, fresh_db):
    with app.app_context():
        onec.set_setting("onec_url", "http://127.0.0.1:9/none")
        assert "недоступен" in onec.run_sync(None)["message"]


def test_admin_new_user_rejects_password_equal_to_login(as_admin):
    """Администратор не может создать пользователя с паролем, равным логину."""
    data = {"login": "Same_Login1", "full_name": "Нормальное Имя", "email": "", "role_id": 3,
            "faculty_id": "", "password": "same_login1"}
    html = post(as_admin, "/admin/users/new", data).get_data(as_text=True)
    assert "не должен совпадать с логином" in html


def test_audit_csv_export(as_admin, fresh_db):
    """Администратор скачивает журнал аудита в CSV; фильтр по действию учитывается."""
    response = as_admin.get("/admin/audit.csv?action=login")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
    lines = response.get_data(as_text=True).lstrip("\ufeff").splitlines()
    assert lines[0] == "Время;Пользователь;Действие;Подробности;IP"
    assert len(lines) >= 2 and all(";login;" in line for line in lines[1:])


def test_audit_csv_forbidden_for_dean(as_dean):
    """Декан не имеет доступа к выгрузке журнала аудита."""
    assert as_dean.get("/admin/audit.csv").status_code == 403