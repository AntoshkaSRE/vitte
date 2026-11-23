"""Вспомогательные функции представлений: рендеринг страниц с «хлебными крошками»."""
from flask import render_template


def page(template: str, crumbs: list | None = None, **context):
    """Отрисовывает шаблон и передаёт в него цепочку «хлебных крошек».

    crumbs — список пар (название, адрес); у последнего элемента адрес
    можно не указывать (None): он выводится как текущая страница.
    Первая крошка «Главная» добавляется базовым шаблоном автоматически.
    """
    return render_template(template, crumbs=crumbs or [], **context)


def to_int(value, default=None):
    """Безопасно преобразует строку параметра запроса в число."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
