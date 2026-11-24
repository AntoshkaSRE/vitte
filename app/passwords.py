"""Единые требования к надёжности пароля (кабинет пользователя и панель администратора)."""

MIN_LENGTH = 8
# Самые распространённые пароли, которые запрещено использовать
COMMON_PASSWORDS = {
    "password", "password1", "qwerty123", "qwertyui", "12345678", "123456789", "1234567890",
    "11111111", "qazwsxedc", "iloveyou", "admin123", "admin1234", "qwerty12", "1q2w3e4r",
}


def check_strength(password: str, login: str = "") -> str | None:
    """Возвращает текст ошибки, если пароль не соответствует требованиям, иначе None.

    Требования: не менее 8 символов; не только цифры и не только буквы;
    не совпадает с логином и не входит в список распространённых паролей.
    """
    if len(password) < MIN_LENGTH:
        return f"Пароль должен содержать не менее {MIN_LENGTH} символов."
    if password.isdigit() or password.isalpha():
        return "Пароль должен сочетать буквы и цифры или символы."
    if login and password.lower() == login.lower():
        return "Пароль не должен совпадать с логином."
    if password.lower() in COMMON_PASSWORDS:
        return "Этот пароль слишком распространён, выберите другой."
    return None
