-- =====================================================================
-- Витте-Дашборд: модуль визуализации данных для единого центра
-- статистических данных ЧОУ ВО «Московский университет им. С.Ю. Витте».
-- Схема базы данных PostgreSQL (физическая модель).
-- Автор: Новоселов Антон Андреевич.
-- =====================================================================

-- Скрипт идемпотентен: перед созданием удаляем прежние объекты.
DROP TABLE IF EXISTS audit_log, uploaded_files, report_history, feedback_messages,
    news, cache_entries, sync_log, integration_settings, dashboard_widgets,
    dashboards, indicator_values, group_performance, indicators, academic_periods,
    study_groups, directions, departments, users, faculties, roles CASCADE;

-- 1. Роли пользователей (ролевая модель доступа)
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20)  NOT NULL UNIQUE,   -- admin / leadership / umu / dean
    name        VARCHAR(80)  NOT NULL,          -- человекочитаемое название
    description TEXT         NOT NULL DEFAULT '',
    level       SMALLINT     NOT NULL DEFAULT 1 -- чем больше, тем шире права
);

-- 2. Факультеты (институты) университета
CREATE TABLE faculties (
    id         SERIAL PRIMARY KEY,
    code       VARCHAR(10)  NOT NULL UNIQUE,
    name       VARCHAR(160) NOT NULL,
    short_name VARCHAR(40)  NOT NULL,
    dean_name  VARCHAR(120) NOT NULL DEFAULT '',
    description TEXT        NOT NULL DEFAULT ''
);

-- 3. Пользователи системы
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    login         VARCHAR(40)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(120) NOT NULL,
    email         VARCHAR(120) NOT NULL DEFAULT '',
    role_id       INTEGER      NOT NULL REFERENCES roles(id),
    faculty_id    INTEGER      REFERENCES faculties(id) ON DELETE SET NULL,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    preferences   JSONB        NOT NULL DEFAULT '{}'::jsonb, -- личные настройки кабинета
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    last_login    TIMESTAMP
);

-- 4. Кафедры (принадлежат факультету)
CREATE TABLE departments (
    id         SERIAL PRIMARY KEY,
    faculty_id INTEGER      NOT NULL REFERENCES faculties(id) ON DELETE CASCADE,
    name       VARCHAR(160) NOT NULL,
    head_name  VARCHAR(120) NOT NULL DEFAULT ''
);

-- 5. Направления подготовки
CREATE TABLE directions (
    id         SERIAL PRIMARY KEY,
    faculty_id INTEGER      NOT NULL REFERENCES faculties(id) ON DELETE CASCADE,
    code       VARCHAR(12)  NOT NULL UNIQUE,   -- например 09.03.03
    name       VARCHAR(160) NOT NULL,
    level      VARCHAR(20)  NOT NULL DEFAULT 'Бакалавриат'
);

-- 6. Учебные группы
CREATE TABLE study_groups (
    id           SERIAL PRIMARY KEY,
    direction_id INTEGER     NOT NULL REFERENCES directions(id) ON DELETE CASCADE,
    name         VARCHAR(30) NOT NULL UNIQUE,
    course       SMALLINT    NOT NULL CHECK (course BETWEEN 1 AND 6),
    study_form   VARCHAR(20) NOT NULL DEFAULT 'Очная'
);

-- 7. Учебные периоды (семестры)
CREATE TABLE academic_periods (
    id          SERIAL PRIMARY KEY,
    academic_year VARCHAR(9)  NOT NULL,         -- 2025/2026
    semester    SMALLINT      NOT NULL CHECK (semester IN (1, 2)),
    title       VARCHAR(60)   NOT NULL,
    start_date  DATE          NOT NULL,
    end_date    DATE          NOT NULL,
    UNIQUE (academic_year, semester)
);

-- 8. Справочник статистических показателей
CREATE TABLE indicators (
    id        SERIAL PRIMARY KEY,
    code      VARCHAR(30)  NOT NULL UNIQUE,
    name      VARCHAR(160) NOT NULL,
    unit      VARCHAR(20)  NOT NULL,
    category  VARCHAR(40)  NOT NULL,            -- контингент / успеваемость / кадры ...
    description TEXT       NOT NULL DEFAULT '',
    is_public BOOLEAN      NOT NULL DEFAULT FALSE -- можно ли показывать без авторизации
);

-- 9. Значения показателей по факультетам и периодам (витрина данных из 1С)
CREATE TABLE indicator_values (
    id           SERIAL PRIMARY KEY,
    indicator_id INTEGER       NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    period_id    INTEGER       NOT NULL REFERENCES academic_periods(id) ON DELETE CASCADE,
    faculty_id   INTEGER       NOT NULL REFERENCES faculties(id) ON DELETE CASCADE,
    value        NUMERIC(14,2) NOT NULL,
    updated_at   TIMESTAMP     NOT NULL DEFAULT NOW(),
    UNIQUE (indicator_id, period_id, faculty_id)
);

-- 10. Успеваемость по учебным группам
CREATE TABLE group_performance (
    id            SERIAL PRIMARY KEY,
    group_id      INTEGER      NOT NULL REFERENCES study_groups(id) ON DELETE CASCADE,
    period_id     INTEGER      NOT NULL REFERENCES academic_periods(id) ON DELETE CASCADE,
    students      INTEGER      NOT NULL CHECK (students >= 0),
    avg_grade     NUMERIC(3,2) NOT NULL CHECK (avg_grade BETWEEN 2 AND 5),
    passed_percent NUMERIC(5,2) NOT NULL CHECK (passed_percent BETWEEN 0 AND 100),
    UNIQUE (group_id, period_id)
);

-- 11. Дашборды (информационные панели)
CREATE TABLE dashboards (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(30)  NOT NULL UNIQUE,
    title       VARCHAR(120) NOT NULL,
    description TEXT         NOT NULL DEFAULT '',
    min_role_level SMALLINT  NOT NULL DEFAULT 1 -- минимальный уровень роли для просмотра
);

-- 12. Виджеты дашбордов (не более 5 на панель по ТЗ)
CREATE TABLE dashboard_widgets (
    id           SERIAL PRIMARY KEY,
    dashboard_id INTEGER      NOT NULL REFERENCES dashboards(id) ON DELETE CASCADE,
    indicator_id INTEGER      NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    title        VARCHAR(120) NOT NULL,
    chart_type   VARCHAR(10)  NOT NULL CHECK (chart_type IN ('bar', 'line', 'pie', 'doughnut', 'kpi')),
    position     SMALLINT     NOT NULL DEFAULT 1
);

-- 13. Настройки интеграции с «1С:Предприятие»
CREATE TABLE integration_settings (
    key        VARCHAR(40) PRIMARY KEY,
    value      TEXT        NOT NULL DEFAULT '',
    updated_at TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- 14. Журнал синхронизации с 1С
CREATE TABLE sync_log (
    id          SERIAL PRIMARY KEY,
    started_at  TIMESTAMP   NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    source      VARCHAR(20) NOT NULL,           -- onec-http / onec-file / manual
    status      VARCHAR(10) NOT NULL DEFAULT 'running',
    rows_loaded INTEGER     NOT NULL DEFAULT 0,
    message     TEXT        NOT NULL DEFAULT '',
    started_by  INTEGER     REFERENCES users(id) ON DELETE SET NULL
);

-- 15. Кэш агрегатов (ТЗ: актуальность данных не более 1 часа)
CREATE TABLE cache_entries (
    cache_key  VARCHAR(200) PRIMARY KEY,
    payload    JSONB     NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 16. Новости (публичный раздел)
CREATE TABLE news (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    summary      VARCHAR(400) NOT NULL,
    body         TEXT         NOT NULL,
    published_at TIMESTAMP    NOT NULL DEFAULT NOW(),
    author_id    INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    is_published BOOLEAN      NOT NULL DEFAULT TRUE
);

-- 17. Обращения через форму обратной связи
CREATE TABLE feedback_messages (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(120) NOT NULL,
    email      VARCHAR(120) NOT NULL,
    subject    VARCHAR(160) NOT NULL,
    message    TEXT         NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT NOW(),
    is_processed BOOLEAN    NOT NULL DEFAULT FALSE
);

-- 18. История сформированных отчётов
CREATE TABLE report_history (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(30) NOT NULL,
    params     JSONB       NOT NULL DEFAULT '{}'::jsonb,
    file_format VARCHAR(10) NOT NULL,
    file_name  VARCHAR(200) NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- 19. Файлы, загруженные пользователями (доступ к файловой системе)
CREATE TABLE uploaded_files (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_name VARCHAR(200) NOT NULL,
    stored_name   VARCHAR(80)  NOT NULL UNIQUE,
    size_bytes    INTEGER      NOT NULL,
    uploaded_at   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 20. Журнал аудита действий пользователей
CREATE TABLE audit_log (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER     REFERENCES users(id) ON DELETE SET NULL,
    action     VARCHAR(40) NOT NULL,
    details    TEXT        NOT NULL DEFAULT '',
    ip_address VARCHAR(45) NOT NULL DEFAULT '',
    created_at TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- Индексы для частых выборок дашбордов и журналов
CREATE INDEX idx_values_period_faculty ON indicator_values (period_id, faculty_id);
CREATE INDEX idx_perf_period ON group_performance (period_id);
CREATE INDEX idx_audit_created ON audit_log (created_at DESC);
CREATE INDEX idx_report_user ON report_history (user_id, created_at DESC);
