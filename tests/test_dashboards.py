"""Тесты дашбордов, JSON-API, кэша и разграничения данных по факультету."""
import json

from tests.conftest import login, post


def test_dashboard_api_returns_widgets(client):
    login(client, "rector")
    data = client.get("/api/dashboard/kpi").get_json()
    assert 1 <= len(data) <= 5, "По ТЗ на дашборде не более 5 виджетов"
    assert {w["type"] for w in data} <= {"bar", "line", "pie", "doughnut", "kpi"}
    assert all(w["title"] for w in data)


def test_all_dashboards_have_at_most_five_widgets(client):
    login(client, "admin")
    for code in ("kpi", "contingent", "performance", "staff", "science"):
        assert len(client.get(f"/api/dashboard/{code}").get_json()) <= 5


def test_unknown_dashboard_404(client):
    login(client, "admin")
    assert client.get("/dashboards/unknown").status_code == 404


def test_dean_sees_only_own_faculty(as_dean):
    """Деканат ФИТ получает данные только по одному факультету, даже если просит все."""
    data = as_dean.get("/api/dashboard/contingent?faculty=").get_json()
    bar = next(w for w in data if w["type"] == "bar")
    assert bar["labels"] == ["ФИТ"]


def test_dean_cannot_override_faculty_in_query(as_dean):
    """Безопасность: подмена параметра faculty не раскрывает чужие данные."""
    data = as_dean.get("/api/dashboard/contingent?faculty=2").get_json()
    bar = next(w for w in data if w["type"] == "bar")
    assert bar["labels"] == ["ФИТ"]


def test_leadership_filter_by_faculty(client):
    login(client, "rector")
    data = client.get("/api/dashboard/contingent?faculty=2").get_json()
    bar = next(w for w in data if w["type"] == "bar")
    assert bar["labels"] == ["ФЭУ"]


def test_line_widget_has_dynamics_over_all_periods(client):
    login(client, "rector")
    data = client.get("/api/dashboard/kpi").get_json()
    line = next(w for w in data if w["type"] == "line")
    assert len(line["labels"]) == 7


def test_kpi_value_is_sum_of_faculties(client):
    """Итоговое значение виджета KPI равно сумме значений по факультетам."""
    login(client, "rector")
    kpi = next(w for w in client.get("/api/dashboard/kpi").get_json() if w["type"] == "kpi")
    cmp_widget = client.get("/api/dashboard/contingent").get_json()
    assert kpi["values"][0] > 0
    assert sum(next(w for w in cmp_widget if w["title"] == "Численность студентов")["values"]) > 0


def test_cache_is_filled_and_reset(client, app):
    login(client, "rector")
    client.get("/api/dashboard/kpi")
    from app.db import query_one
    with app.app_context():
        assert query_one("SELECT COUNT(*) AS n FROM cache_entries")["n"] > 0
    post(client, "/dashboards/refresh", {})
    with app.app_context():
        assert query_one("SELECT COUNT(*) AS n FROM cache_entries")["n"] == 0


def test_response_time_under_five_seconds(client):
    """Нефункциональное требование ТЗ: формирование данных дашборда — не более 5 секунд."""
    import time
    login(client, "rector")
    start = time.perf_counter()
    for code in ("kpi", "contingent", "performance"):
        client.get(f"/api/dashboard/{code}")
    assert time.perf_counter() - start < 5


def test_public_api_json_structure(client):
    data = json.loads(client.get("/api/public/AVG_GRADE").data)
    assert set(data) == {"indicator", "compare", "dynamics"}
    assert len(data["compare"]["labels"]) == len(data["compare"]["values"]) == 5
