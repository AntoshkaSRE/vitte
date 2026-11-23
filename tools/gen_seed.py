"""Генератор тестовых данных Витте-Дашборд.

Формирует два согласованных файла:
  * sql/insert_test_data.sql  — начальное наполнение базы данных;
  * data/onec_export.json     — эмуляция ответа HTTP-сервиса 1С:Предприятие.

Данные тестовые (не реальная статистика университета), но структурно и
по порядку величин соответствуют предметной области. Генерация
детерминирована (фиксированное зерно), поэтому результат воспроизводим.
Запуск: python tools/gen_seed.py
"""
import json
import random
from pathlib import Path

from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent.parent
rnd = random.Random(2026)

# ----------------------------- справочники ------------------------------
ROLES = [
    ("admin", "Администратор", "Полный доступ, управление пользователями и интеграцией", 4),
    ("leadership", "Руководство", "Просмотр всех дашбордов и выгрузка отчётов", 3),
    ("umu", "УМУ", "Формирование отчётов учебно-методического управления", 2),
    ("dean", "Деканат", "Просмотр данных своего факультета", 1),
]

FACULTIES = [
    ("FIT", "Факультет информационных технологий", "ФИТ", "Лебедев Сергей Игоревич"),
    ("FEU", "Факультет экономики и управления", "ФЭУ", "Миронова Елена Павловна"),
    ("LAW", "Юридический факультет", "ЮФ", "Ковалёв Дмитрий Андреевич"),
    ("PSY", "Факультет психологии", "ФП", "Соколова Ирина Викторовна"),
    ("DES", "Факультет дизайна и коммуникаций", "ФДК", "Орлов Михаил Сергеевич"),
]

# (код факультета, код направления, название, аббревиатура групп)
DIRECTIONS = [
    ("FIT", "09.03.03", "Прикладная информатика", "ПИ"),
    ("FIT", "09.03.01", "Информатика и вычислительная техника", "ИВТ"),
    ("FIT", "10.03.01", "Информационная безопасность", "ИБ"),
    ("FEU", "38.03.01", "Экономика", "ЭК"),
    ("FEU", "38.03.02", "Менеджмент", "МН"),
    ("FEU", "38.03.04", "Государственное и муниципальное управление", "ГМУ"),
    ("LAW", "40.03.01", "Юриспруденция", "ЮР"),
    ("PSY", "37.03.01", "Психология", "ПС"),
    ("PSY", "44.03.02", "Психолого-педагогическое образование", "ППО"),
    ("DES", "42.03.01", "Реклама и связи с общественностью", "РСО"),
    ("DES", "54.03.01", "Дизайн", "ДЗ"),
    ("FEU", "38.03.05", "Бизнес-информатика", "БИ"),
]

DEPARTMENTS = [
    ("FIT", "Кафедра информационных систем", "Простомолотов Александр Сергеевич"),
    ("FIT", "Кафедра информационной безопасности", "Громов Алексей Петрович"),
    ("FEU", "Кафедра экономики", "Беляева Ольга Николаевна"),
    ("FEU", "Кафедра менеджмента", "Захаров Игорь Юрьевич"),
    ("LAW", "Кафедра гражданского права", "Фролова Татьяна Алексеевна"),
    ("LAW", "Кафедра уголовного права", "Дроздов Николай Васильевич"),
    ("PSY", "Кафедра общей психологии", "Никитина Анна Сергеевна"),
    ("DES", "Кафедра дизайна", "Куликов Артём Олегович"),
    ("DES", "Кафедра рекламы и PR", "Тарасова Марина Игоревна"),
    ("PSY", "Кафедра педагогики", "Воронин Павел Дмитриевич"),
]

# (год начала, семестр, название, начало, конец)
PERIODS = [
    ("2023/2024", 1, "Осенний семестр 2023/2024", "2023-09-01", "2024-01-31"),
    ("2023/2024", 2, "Весенний семестр 2023/2024", "2024-02-01", "2024-06-30"),
    ("2024/2025", 1, "Осенний семестр 2024/2025", "2024-09-01", "2025-01-31"),
    ("2024/2025", 2, "Весенний семестр 2024/2025", "2025-02-01", "2025-06-30"),
    ("2025/2026", 1, "Осенний семестр 2025/2026", "2025-09-01", "2026-01-31"),
    ("2025/2026", 2, "Весенний семестр 2025/2026", "2026-02-01", "2026-06-30"),
    ("2026/2027", 1, "Осенний семестр 2026/2027", "2026-09-01", "2027-01-31"),
]

# (код, название, единица, категория, описание, публичный)
INDICATORS = [
    ("STUDENTS_TOTAL", "Численность студентов", "чел.", "Контингент", "Общее число обучающихся на начало периода", True),
    ("STUDENTS_FULLTIME", "Студенты очной формы", "чел.", "Контингент", "Число обучающихся по очной форме", True),
    ("STUDENTS_PARTTIME", "Студенты заочной и очно-заочной форм", "чел.", "Контингент", "Число обучающихся по заочной и очно-заочной формам", False),
    ("ADMITTED", "Принято на первый курс", "чел.", "Контингент", "Приём на первый курс за период", True),
    ("EXPELLED", "Отчислено студентов", "чел.", "Контингент", "Число отчисленных за период", False),
    ("GRADUATES", "Выпуск", "чел.", "Контингент", "Число выпускников за период", True),
    ("AVG_GRADE", "Средний балл по итогам сессии", "балл", "Успеваемость", "Средневзвешенный балл по студентам факультета", True),
    ("PASS_RATE", "Доля студентов без задолженностей", "%", "Успеваемость", "Доля сдавших сессию в срок", True),
    ("STAFF_TOTAL", "Численность профессорско-преподавательского состава", "чел.", "Кадры", "Штатные и совместители, пересчёт на физические лица", False),
    ("STAFF_DEGREE", "Доля ППС с учёной степенью", "%", "Кадры", "Кандидаты и доктора наук от общего числа ППС", True),
    ("LOAD_HOURS", "Плановая учебная нагрузка", "час.", "Нагрузка", "Суммарная плановая нагрузка кафедр факультета", False),
    ("PUBLICATIONS", "Научные публикации", "шт.", "Наука", "Публикации ППС в РИНЦ за период", False),
]

# (код, название, описание, мин. уровень роли, [(показатель, заголовок, тип графика)])
DASHBOARDS = [
    ("kpi", "Ключевые показатели деятельности университета",
     "Сводные показатели для руководства: контингент, успеваемость, кадры.", 3,
     [("STUDENTS_TOTAL", "Численность студентов по факультетам", "bar"),
      ("AVG_GRADE", "Динамика среднего балла", "line"),
      ("PASS_RATE", "Доля студентов без задолженностей", "bar"),
      ("STAFF_DEGREE", "Доля ППС с учёной степенью", "doughnut"),
      ("ADMITTED", "Приём на первый курс", "kpi")]),
    ("contingent", "Контингент студентов",
     "Структура и движение контингента по факультетам и периодам.", 1,
     [("STUDENTS_TOTAL", "Численность студентов", "bar"),
      ("STUDENTS_FULLTIME", "Структура очной формы", "pie"),
      ("ADMITTED", "Приём на первый курс", "line"),
      ("EXPELLED", "Отчисленные студенты", "bar"),
      ("GRADUATES", "Выпуск", "kpi")]),
    ("performance", "Успеваемость",
     "Успеваемость студентов по итогам сессий.", 1,
     [("AVG_GRADE", "Средний балл", "line"),
      ("PASS_RATE", "Доля студентов без задолженностей", "bar"),
      ("EXPELLED", "Отчисления за период", "bar")]),
    ("staff", "Кадровый состав и нагрузка",
     "Профессорско-преподавательский состав и учебная нагрузка.", 2,
     [("STAFF_TOTAL", "Численность ППС", "bar"),
      ("STAFF_DEGREE", "Доля ППС с учёной степенью", "line"),
      ("LOAD_HOURS", "Плановая учебная нагрузка", "bar")]),
    ("science", "Научная деятельность",
     "Публикационная активность преподавателей.", 2,
     [("PUBLICATIONS", "Научные публикации", "bar"),
      ("STAFF_TOTAL", "Численность ППС", "pie")]),
]

USERS = [
    ("admin", "Admin#2026", "Новоселов Антон Андреевич", "admin@vitte.local", "admin", None),
    ("rector", "Rector#2026", "Петров Владимир Николаевич", "rector@vitte.local", "leadership", None),
    ("umu", "Umu#2026", "Иванова Светлана Михайловна", "umu@vitte.local", "umu", None),
    ("dean_fit", "Dean#2026", "Лебедев Сергей Игоревич", "dean.fit@vitte.local", "dean", "FIT"),
    ("dean_feu", "Dean#2026", "Миронова Елена Павловна", "dean.feu@vitte.local", "dean", "FEU"),
    ("dean_law", "Dean#2026", "Ковалёв Дмитрий Андреевич", "dean.law@vitte.local", "dean", "LAW"),
]

NEWS = [
    ("Запущена пробная версия модуля визуализации данных",
     "Кафедра информационных систем начала опытную эксплуатацию модуля Витте-Дашборд.",
     "Модуль подключается к единому центру статистических данных и строит интерактивные дашборды без ручной выгрузки в Excel. Опытная эксплуатация продлится пять рабочих дней."),
    ("Дашборд «Ключевые показатели» доступен руководству",
     "Ректорат получил сводную панель из пяти ключевых показателей.",
     "На панели отображаются численность студентов, динамика среднего балла, доля студентов без задолженностей, доля преподавателей со степенью и приём на первый курс."),
    ("Экспорт отчётов в Word и Excel",
     "Сотрудники УМУ могут выгружать отчёты в форматах DOCX и XLSX.",
     "В разделе «Отчёты» выбирается тип отчёта, период и факультет. История выгрузок сохраняется в личном кабинете пользователя."),
    ("Автоматическая синхронизация с 1С:Предприятие",
     "Данные обновляются по кнопке «Обновить» и по расписанию — раз в час.",
     "Администратор настраивает адрес HTTP-сервиса 1С в панели администратора и контролирует журнал синхронизации."),
    ("Разграничение прав доступа по ролям",
     "В системе работают четыре роли: администратор, руководство, УМУ и деканат.",
     "Деканат видит данные только своего факультета, руководство — все дашборды, а администратор управляет пользователями и справочниками."),
    ("Инструктаж для пользователей модуля",
     "Для сотрудников УМУ пройдёт двухчасовой инструктаж.",
     "Участникам будет выдано краткое руководство пользователя. Запись на инструктаж — через форму обратной связи."),
]

FEEDBACK = [
    ("Смирнова Анна", "smirnova@example.com", "Вопрос по доступу", "Подскажите, как получить доступ к дашборду успеваемости?"),
    ("Козлов Игорь", "kozlov@example.com", "Предложение", "Хорошо бы добавить диаграмму по формам обучения."),
    ("Фёдорова Мария", "fedorova@example.com", "Ошибка в данных", "В показателе приёма на 2 курсе видна неточность."),
]

# ---------------------------- генерация данных --------------------------
def sql_str(value):
    """Экранирует строку для вставки в SQL-литерал."""
    return "'" + str(value).replace("'", "''") + "'"


def build_groups():
    """Создаёт учебные группы: по четыре курса для шести направлений, по два — для остальных."""
    groups = []
    for idx, (fac, code, name, abbr) in enumerate(DIRECTIONS):
        courses = [1, 2, 3, 4] if idx < 6 else [1, 3]
        for course in courses:
            year = 26 - course
            groups.append((code, f"{abbr}-{year}1", course, "Очная"))
        if idx % 3 == 0:
            groups.append((code, f"{abbr}-{25 - 2}З", 3, "Заочная"))
    return groups


def main():
    groups = build_groups()
    fac_by_dir = {d[1]: d[0] for d in DIRECTIONS}
    # Базовая численность и качество группы — постоянны, к ним добавляется шум по периодам
    base = {g[1]: (rnd.randint(18, 34), rnd.uniform(3.6, 4.5), rnd.uniform(78, 96)) for g in groups}
    perf_rows = []   # (группа, период индекс, студентов, балл, % сдавших)
    for g in groups:
        students, grade, passed = base[g[1]]
        for p_idx in range(len(PERIODS)):
            drift = p_idx * 0.02
            perf_rows.append((
                g[1], p_idx,
                max(8, students + rnd.randint(-2, 2) + (p_idx // 3)),
                round(min(4.95, grade + rnd.uniform(-0.12, 0.12) + drift), 2),
                round(min(99.5, passed + rnd.uniform(-3, 3) + p_idx * 0.3), 2),
            ))
    # Агрегаты по факультетам считаются из групповых данных, чтобы цифры были согласованы
    values = []  # (показатель, период индекс, код факультета, значение)
    for p_idx in range(len(PERIODS)):
        for fac in FACULTIES:
            rows = [r for r in perf_rows
                    if r[1] == p_idx and fac_by_dir[next(g[0] for g in groups if g[1] == r[0])] == fac[0]]
            total = sum(r[2] for r in rows)
            weighted_grade = sum(r[2] * r[3] for r in rows) / total
            weighted_pass = sum(r[2] * r[4] for r in rows) / total
            fulltime = round(total * rnd.uniform(0.62, 0.78))
            # Для ПС-периодов (весенних) выпуск и отчисления выше
            is_spring = PERIODS[p_idx][1] == 2
            staff = max(12, round(total / rnd.uniform(9, 12)))
            values.extend([
                ("STUDENTS_TOTAL", p_idx, fac[0], total),
                ("STUDENTS_FULLTIME", p_idx, fac[0], fulltime),
                ("STUDENTS_PARTTIME", p_idx, fac[0], total - fulltime),
                ("ADMITTED", p_idx, fac[0], 0 if is_spring else round(total * rnd.uniform(0.22, 0.3))),
                ("EXPELLED", p_idx, fac[0], round(total * rnd.uniform(0.01, 0.045))),
                ("GRADUATES", p_idx, fac[0], round(total * rnd.uniform(0.18, 0.24)) if is_spring else 0),
                ("AVG_GRADE", p_idx, fac[0], round(weighted_grade, 2)),
                ("PASS_RATE", p_idx, fac[0], round(weighted_pass, 2)),
                ("STAFF_TOTAL", p_idx, fac[0], staff),
                ("STAFF_DEGREE", p_idx, fac[0], round(rnd.uniform(48, 72) + p_idx * 0.6, 1)),
                ("LOAD_HOURS", p_idx, fac[0], staff * rnd.randint(640, 760)),
                ("PUBLICATIONS", p_idx, fac[0], round(staff * rnd.uniform(0.8, 1.6))),
            ])

    lines = ["-- Тестовые данные Витте-Дашборд (сформированы tools/gen_seed.py). Не редактировать вручную.",
             "SET client_encoding = 'UTF8';", ""]

    def insert(table, columns, rows):
        """Добавляет многострочную команду INSERT в итоговый скрипт."""
        lines.append(f"INSERT INTO {table} ({', '.join(columns)}) VALUES")
        lines.append(",\n".join("  (" + ", ".join(r) + ")" for r in rows) + ";")
        lines.append("")

    insert("roles", ["code", "name", "description", "level"],
           [[sql_str(r[0]), sql_str(r[1]), sql_str(r[2]), str(r[3])] for r in ROLES])
    insert("faculties", ["code", "name", "short_name", "dean_name", "description"],
           [[sql_str(f[0]), sql_str(f[1]), sql_str(f[2]), sql_str(f[3]),
             sql_str(f"{f[1]} — структурное подразделение университета.")] for f in FACULTIES])
    insert("departments", ["faculty_id", "name", "head_name"],
           [[f"(SELECT id FROM faculties WHERE code={sql_str(d[0])})", sql_str(d[1]), sql_str(d[2])]
            for d in DEPARTMENTS])
    insert("directions", ["faculty_id", "code", "name", "level"],
           [[f"(SELECT id FROM faculties WHERE code={sql_str(d[0])})", sql_str(d[1]), sql_str(d[2]),
             sql_str("Бакалавриат")] for d in DIRECTIONS])
    insert("study_groups", ["direction_id", "name", "course", "study_form"],
           [[f"(SELECT id FROM directions WHERE code={sql_str(g[0])})", sql_str(g[1]), str(g[2]), sql_str(g[3])]
            for g in groups])
    insert("academic_periods", ["academic_year", "semester", "title", "start_date", "end_date"],
           [[sql_str(p[0]), str(p[1]), sql_str(p[2]), sql_str(p[3]), sql_str(p[4])] for p in PERIODS])
    insert("indicators", ["code", "name", "unit", "category", "description", "is_public"],
           [[sql_str(i[0]), sql_str(i[1]), sql_str(i[2]), sql_str(i[3]), sql_str(i[4]),
             "TRUE" if i[5] else "FALSE"] for i in INDICATORS])

    def period_id(idx):
        """Подзапрос идентификатора периода по его порядковому номеру."""
        p = PERIODS[idx]
        return f"(SELECT id FROM academic_periods WHERE academic_year={sql_str(p[0])} AND semester={p[1]})"

    insert("indicator_values", ["indicator_id", "period_id", "faculty_id", "value"],
           [[f"(SELECT id FROM indicators WHERE code={sql_str(v[0])})", period_id(v[1]),
             f"(SELECT id FROM faculties WHERE code={sql_str(v[2])})", str(v[3])] for v in values])
    insert("group_performance", ["group_id", "period_id", "students", "avg_grade", "passed_percent"],
           [[f"(SELECT id FROM study_groups WHERE name={sql_str(r[0])})", period_id(r[1]),
             str(r[2]), str(r[3]), str(r[4])] for r in perf_rows])
    insert("dashboards", ["code", "title", "description", "min_role_level"],
           [[sql_str(d[0]), sql_str(d[1]), sql_str(d[2]), str(d[3])] for d in DASHBOARDS])
    widget_rows = []
    for d in DASHBOARDS:
        for pos, (ind, title, ctype) in enumerate(d[4], start=1):
            widget_rows.append([f"(SELECT id FROM dashboards WHERE code={sql_str(d[0])})",
                                f"(SELECT id FROM indicators WHERE code={sql_str(ind)})",
                                sql_str(title), sql_str(ctype), str(pos)])
    insert("dashboard_widgets", ["dashboard_id", "indicator_id", "title", "chart_type", "position"], widget_rows)
    insert("users", ["login", "password_hash", "full_name", "email", "role_id", "faculty_id"],
           [[sql_str(u[0]), sql_str(generate_password_hash(u[1], method="pbkdf2:sha256")), sql_str(u[2]),
             sql_str(u[3]), f"(SELECT id FROM roles WHERE code={sql_str(u[4])})",
             f"(SELECT id FROM faculties WHERE code={sql_str(u[5])})" if u[5] else "NULL"] for u in USERS])
    insert("news", ["title", "summary", "body", "published_at", "author_id"],
           [[sql_str(n[0]), sql_str(n[1]), sql_str(n[2]),
             f"NOW() - INTERVAL '{i * 3} days'", "(SELECT id FROM users WHERE login='admin')"]
            for i, n in enumerate(NEWS)])
    insert("feedback_messages", ["name", "email", "subject", "message"],
           [[sql_str(x) for x in f] for f in FEEDBACK])
    insert("integration_settings", ["key", "value"],
           [[sql_str("onec_url"), sql_str("")], [sql_str("onec_login"), sql_str("stat_reader")],
            [sql_str("sync_interval_minutes"), sql_str("60")], [sql_str("onec_base"), sql_str("UniversityStat")]])
    insert("sync_log", ["started_at", "finished_at", "source", "status", "rows_loaded", "message", "started_by"],
           [[f"NOW() - INTERVAL '{h} hours'", f"NOW() - INTERVAL '{h} hours' + INTERVAL '4 seconds'",
             sql_str("onec-file"), sql_str("ok"), str(len(values)), sql_str("Тестовая загрузка завершена"),
             "(SELECT id FROM users WHERE login='admin')"] for h in (1, 25, 49)])
    insert("report_history", ["user_id", "report_type", "params", "file_format", "file_name"],
           [["(SELECT id FROM users WHERE login='umu')", sql_str("performance"),
             sql_str('{"period": 5, "faculty": "all"}') + "::jsonb", sql_str("xlsx"), sql_str("performance_example.xlsx")],
            ["(SELECT id FROM users WHERE login='rector')", sql_str("contingent"),
             sql_str('{"period": 7, "faculty": "all"}') + "::jsonb", sql_str("docx"), sql_str("contingent_example.docx")]])
    insert("audit_log", ["user_id", "action", "details", "ip_address"],
           [["(SELECT id FROM users WHERE login='admin')", sql_str("login"), sql_str("Вход в систему"), sql_str("127.0.0.1")],
            ["(SELECT id FROM users WHERE login='umu')", sql_str("report"), sql_str("Отчёт performance (xlsx)"), sql_str("127.0.0.1")]])

    (ROOT / "sql" / "insert_test_data.sql").write_text("\n".join(lines), encoding="utf-8")

    # Файл-эмулятор ответа сервиса 1С: тот же набор показателей в виде JSON
    export = {
        "source": "UniversityStat (эмулятор ответа HTTP-сервиса 1С:Предприятие)",
        "values": [{"indicator": v[0], "period": f"{PERIODS[v[1]][0]}-{PERIODS[v[1]][1]}",
                    "faculty": v[2], "value": v[3]} for v in values],
    }
    (ROOT / "data" / "onec_export.json").write_text(
        json.dumps(export, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Групп: {len(groups)}, показателей: {len(values)}, строк успеваемости: {len(perf_rows)}")


if __name__ == "__main__":
    main()
