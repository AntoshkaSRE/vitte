"""Модульные тесты проверки надёжности пароля."""
import pytest

from app.passwords import check_strength


@pytest.mark.parametrize("password", ["Admin#2026", "Rector#2026", "abc12345", "Zq9!zq9!"])
def test_strong_passwords_accepted(password):
    assert check_strength(password) is None


@pytest.mark.parametrize("password, fragment", [
    ("short1", "не менее 8"),
    ("12345678", "буквы и цифры"),
    ("abcdefghij", "буквы и цифры"),
    ("Password1", "распространён"),
    ("QWERTY123", "распространён"),
])
def test_weak_passwords_rejected(password, fragment):
    assert fragment in check_strength(password)


def test_password_equal_to_login_rejected():
    """Пароль, совпадающий с логином (без учёта регистра), запрещён."""
    assert "логином" in check_strength("Dean_FIT_01", login="dean_fit_01")
    assert check_strength("Dean_FIT_01", login="other_user") is None
