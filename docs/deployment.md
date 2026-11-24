# Развёртывание Витте-Дашборд

## Локальный запуск

Требуется Python 3.12 и PostgreSQL 14 или новее.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # при необходимости изменить DATABASE_URL
python tools/init_db.py     # создаёт базу, 20 таблиц и тестовые данные
python main.py              # http://127.0.0.1:5000
```

Проверка: страница http://127.0.0.1:5000/healthz должна вернуть `{"database": "ok", "status": "ok", ...}`.

## Переменные окружения

| Переменная | Назначение | Значение по умолчанию |
|---|---|---|
| `DATABASE_URL` | строка подключения к PostgreSQL | локальная база `vitte` |
| `SECRET_KEY` | ключ подписи сессий (в продуктивной среде обязательно заменить) | `dev-secret-key-change-me` |
| `COOKIE_SECURE` | `1` — cookie сессии передаётся только по HTTPS | `0` |
| `LOGIN_MAX_ATTEMPTS` | число неудачных попыток входа до блокировки | `5` |
| `LOGIN_WINDOW_SECONDS` | окно подсчёта неудачных попыток, секунд | `300` |
| `ONEC_URL` | адрес HTTP-сервиса 1С; пусто — файл `data/onec_export.json` | пусто |
| `CACHE_TTL` | время жизни кэша агрегатов, секунд | `3600` |

## Бесплатный хостинг Render

Размещение описано в `render.yaml` (Blueprint): веб-сервис `vitte` и база данных `vitte-db` тарифа Free.

1. Войти в Render (https://render.com) и выбрать **New → Blueprint**.
2. Указать репозиторий `AntoshkaSRE/vitte`, ветку `master`.
3. Render создаст базу и сервис. При сборке выполняется `pip install -r requirements.txt && python tools/init_db.py`,
   запуск — `gunicorn main:app --bind 0.0.0.0:$PORT --workers 2`.
4. Адрес сервиса проверяется по `/healthz`; `SECRET_KEY` генерируется автоматически, `DATABASE_URL` берётся из базы.
5. После каждого коммита в `master` Render пересобирает сервис автоматически.

Ограничения бесплатного тарифа: сервис «засыпает» после 15 минут без запросов (первое обращение после простоя занимает
до минуты), а бесплатная база данных Render удаляется через 30 дней после создания, поэтому её нужно пересоздавать.

## Тестирование

```powershell
python -m pytest -q         # 172 теста, нужна доступная PostgreSQL (создаётся база vitte_test)
```