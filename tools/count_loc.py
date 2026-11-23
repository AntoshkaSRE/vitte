"""Подсчёт логических строк собственного кода проекта.

Не учитываются: пустые строки, строки комментариев, строки только с управляющими
символами (скобки, `end`-теги), сторонняя библиотека Chart.js и автоматически
сгенерированные файлы (sql/insert_test_data.sql, sql/vitte_dump.sql, data/onec_export.json).
Запуск: python tools/count_loc.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE = {"vendor", ".venv", "__pycache__", ".git", "instance"}
GENERATED = {"insert_test_data.sql", "vitte_dump.sql", "onec_export.json"}
# Строки, состоящие только из управляющих символов
CONTROL_ONLY = re.compile(r"^[\s{}()\[\];,]*$")


def logical_lines(path: Path) -> int:
    """Считает значимые строки файла с учётом синтаксиса комментариев его типа."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix
    if suffix == ".html":
        text = re.sub(r"\{#.*?#\}", "", text, flags=re.S)       # комментарии Jinja
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)       # комментарии HTML
    if suffix in (".css", ".js"):
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)        # блочные комментарии
    count, in_doc = 0, False
    for raw in text.splitlines():
        line = raw.strip()
        if suffix == ".py":
            # Строки документации (docstring) относятся к комментариям
            quotes = line.count('"""')
            if in_doc:
                if quotes:
                    in_doc = False
                continue
            if line.startswith('"""'):
                if quotes == 1:
                    in_doc = True
                continue
            if line.startswith("#"):
                continue
        elif suffix in (".js",) and line.startswith("//"):
            continue
        elif suffix == ".sql" and line.startswith("--"):
            continue
        if not line or CONTROL_ONLY.match(line):
            continue
        count += 1
    return count


def main() -> None:
    totals: dict[str, int] = {}
    files = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in (".py", ".html", ".css", ".js", ".sql"):
            continue
        if EXCLUDE & set(path.relative_to(ROOT).parts) or path.name in GENERATED:
            continue
        group = "tests" if "tests" in path.parts else path.suffix
        totals[group] = totals.get(group, 0) + logical_lines(path)
        files += 1
    for group, value in sorted(totals.items()):
        print(f"{group:8} {value:6}")
    own = sum(v for k, v in totals.items() if k != "tests")
    print(f"Файлов: {files}; логических строк без тестов: {own}; вместе с тестами: {sum(totals.values())}")


if __name__ == "__main__":
    main()
