"""Тесты отчётов (XLSX/DOCX/CSV), личного кабинета и работы с файлами."""
import io
import zipfile

import pytest
from openpyxl import load_workbook

from tests.conftest import login, post


@pytest.mark.parametrize("fmt,signature", [("xlsx", b"PK"), ("docx", b"PK"), ("csv", b"\xef\xbb\xbf")])
@pytest.mark.parametrize("rtype", ["performance", "summary"])
def test_report_generation(client, rtype, fmt, signature, fresh_db):
    login(client, "umu")
    response = post(client, "/reports/generate", {"report_type": rtype, "period": 5, "faculty": "", "format": fmt})
    assert response.status_code == 200
    assert response.data.startswith(signature)


def test_xlsx_content(client, fresh_db):
    login(client, "umu")
    response = post(client, "/reports/generate", {"report_type": "performance", "period": 5, "format": "xlsx"})
    ws = load_workbook(io.BytesIO(response.data)).active
    assert ws["A1"].value.startswith("Успеваемость по учебным группам")
    assert ws["A4"].value == "Факультет"
    assert ws.max_row > 10


def test_docx_is_valid_zip(client, fresh_db):
    login(client, "rector")
    response = post(client, "/reports/generate", {"report_type": "summary", "period": 7, "format": "docx"})
    assert "word/document.xml" in zipfile.ZipFile(io.BytesIO(response.data)).namelist()


def test_report_invalid_params(client):
    login(client, "umu")
    response = post(client, "/reports/generate", {"report_type": "evil", "period": 5, "format": "xlsx"})
    assert response.status_code == 302


def test_report_unknown_period(client):
    login(client, "umu")
    assert post(client, "/reports/generate", {"report_type": "summary", "period": 999, "format": "csv"}).status_code == 404


def test_dean_report_restricted_to_faculty(as_dean, fresh_db):
    response = post(as_dean, "/reports/generate", {"report_type": "summary", "period": 5, "faculty": "2", "format": "csv"})
    text = response.data.decode("utf-8-sig")
    assert "ФИТ" in text and "ФЭУ" not in text


def test_report_saved_in_history(client, fresh_db):
    login(client, "umu")
    post(client, "/reports/generate", {"report_type": "summary", "period": 5, "format": "csv"})
    assert ".csv" in client.get("/cabinet/reports").get_data(as_text=True)


def test_cabinet_pages_open(as_admin):
    for url in ("/cabinet/", "/cabinet/profile", "/cabinet/password", "/cabinet/reports",
                "/cabinet/files", "/cabinet/settings"):
        assert as_admin.get(url).status_code == 200


def test_profile_update(client, fresh_db):
    login(client, "umu")
    post(client, "/cabinet/profile", {"full_name": "Иванова Светлана Петровна", "email": "new@example.com"})
    assert "Иванова Светлана Петровна" in client.get("/cabinet/").get_data(as_text=True)


def test_profile_validation(client):
    login(client, "umu")
    html = post(client, "/cabinet/profile", {"full_name": "Ив", "email": "bad"}).get_data(as_text=True)
    assert 'class="errors"' in html


@pytest.mark.parametrize("new,again,old", [("short1", "short1", "Umu#2026"), ("12345678", "12345678", "Umu#2026"),
                                           ("Good#Pass1", "Other#Pass1", "Umu#2026"), ("Good#Pass1", "Good#Pass1", "wrong")])
def test_password_change_rejected(client, new, again, old):
    login(client, "umu")
    html = post(client, "/cabinet/password", {"old": old, "new": new, "again": again}).get_data(as_text=True)
    assert 'class="errors"' in html


def test_password_change_ok(client, fresh_db):
    login(client, "umu")
    response = post(client, "/cabinet/password", {"old": "Umu#2026", "new": "NewPass#2027", "again": "NewPass#2027"})
    assert response.status_code == 302
    other = client.application.test_client()
    assert post(other, "/login", {"login": "umu", "password": "NewPass#2027"}).status_code == 302


def test_settings_saved_and_theme_applied(client, fresh_db):
    login(client, "umu")
    post(client, "/cabinet/settings", {"period": 3, "chart": "line", "theme": "dark"})
    assert 'data-theme="dark"' in client.get("/cabinet/").get_data(as_text=True)


def test_file_upload_download_delete(client, fresh_db):
    login(client, "umu")
    data = {"file": (io.BytesIO("тест".encode()), "заметка.txt"), "csrf_token": "x"}
    from tests.conftest import csrf
    data["csrf_token"] = csrf(client)
    response = client.post("/cabinet/files", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert "загружен" in response.get_data(as_text=True)
    page = client.get("/cabinet/files").get_data(as_text=True)
    assert "txt" in page or "заметка" in page
    assert client.get("/cabinet/files/1/download").status_code == 200
    assert post(client, "/cabinet/files/1/delete").status_code == 302
    assert client.get("/cabinet/files/1/download").status_code == 404


def test_file_upload_forbidden_extension(client):
    login(client, "umu")
    from tests.conftest import csrf
    data = {"file": (io.BytesIO(b"MZ"), "virus.exe"), "csrf_token": csrf(client)}
    response = client.post("/cabinet/files", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert "Недопустимый тип файла" in response.get_data(as_text=True)


def test_files_isolated_between_users(client, fresh_db):
    from tests.conftest import csrf
    login(client, "umu")
    client.post("/cabinet/files", data={"file": (io.BytesIO(b"abc"), "a.txt"), "csrf_token": csrf(client)},
                content_type="multipart/form-data")
    other = client.application.test_client()
    login(other, "rector")
    assert other.get("/cabinet/files/1/download").status_code == 404
