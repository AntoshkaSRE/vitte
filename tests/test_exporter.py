"""Модульные тесты вспомогательных функций выгрузки (без обращения к базе данных)."""
import pytest

from app.services.exporter import csv_safe, to_csv


@pytest.mark.parametrize("value", ["=SUM(A1:A9)", "+7900", "-1+1", "@cmd", "\tтекст"])
def test_csv_safe_neutralizes_formulas(value):
    """Строки, которые Excel воспримет как формулу, получают ведущий апостроф."""
    assert csv_safe(value) == "'" + value


@pytest.mark.parametrize("value", ["Вход в систему", "admin", "", 42, -5, 3.5, None])
def test_csv_safe_keeps_normal_values(value):
    """Обычный текст, числа и пустые значения остаются без изменений."""
    assert csv_safe(value) == value


def test_to_csv_utf8_bom_and_semicolon():
    """CSV сохраняется в UTF-8 с BOM и разделителем «;» для корректного открытия в Excel."""
    data = to_csv(["Показатель", "Значение"], [["Выпуск", 12]])
    assert data.startswith(b"\xef\xbb\xbf")
    assert data.decode("utf-8-sig").splitlines() == ["Показатель;Значение", "Выпуск;12"]