"""Нагрузочное тестирование Витте-Дашборд.

Имитирует одновременную работу нескольких пользователей: каждый входит в систему
и многократно запрашивает главную страницу и данные дашбордов. Выводит время
отклика (среднее, 95-й процентиль, максимум) и число ошибок.
Запуск при работающем приложении: python tools/load_test.py [пользователей] [запросов]
"""
import http.cookiejar
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:5000"
PAGES = ["/", "/open-stats", "/api/public/STUDENTS_TOTAL", "/api/dashboard/kpi",
         "/api/dashboard/performance", "/dashboards/contingent"]

timings: list[float] = []
errors: list[str] = []
lock = threading.Lock()


def worker(requests_count: int) -> None:
    """Один виртуальный пользователь: вход под ролью «Руководство» и серия запросов."""
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    html = opener.open(f"{BASE}/login").read().decode()
    token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    data = urllib.parse.urlencode({"login": "rector", "password": "Rector#2026", "csrf_token": token}).encode()
    opener.open(f"{BASE}/login", data)
    for i in range(requests_count):
        url = BASE + PAGES[i % len(PAGES)]
        start = time.perf_counter()
        try:
            opener.open(url).read()
            elapsed = time.perf_counter() - start
            with lock:
                timings.append(elapsed)
        except urllib.error.URLError as exc:
            with lock:
                errors.append(f"{url}: {exc}")


def main() -> None:
    users = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    per_user = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    threads = [threading.Thread(target=worker, args=(per_user,)) for _ in range(users)]
    started = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = time.perf_counter() - started
    timings.sort()
    p95 = timings[int(len(timings) * 0.95) - 1] if timings else 0
    print(f"Пользователей: {users}, запросов: {len(timings) + len(errors)}, ошибок: {len(errors)}")
    print(f"Общее время: {total:.2f} с, пропускная способность: {len(timings) / total:.1f} запр./с")
    if timings:
        print(f"Отклик, мс: среднее {statistics.mean(timings) * 1000:.0f}, "
              f"медиана {statistics.median(timings) * 1000:.0f}, p95 {p95 * 1000:.0f}, максимум {timings[-1] * 1000:.0f}")
    for line in errors[:5]:
        print("Ошибка:", line)


if __name__ == "__main__":
    main()
