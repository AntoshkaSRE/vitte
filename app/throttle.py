"""Ограничение числа неудачных попыток входа (защита от подбора пароля).

Счётчик хранится в памяти процесса: при перезапуске сервиса он обнуляется,
а при нескольких процессах gunicorn у каждого процесса он свой. Для учебного
модуля этого достаточно, для промышленной эксплуатации счётчик переносят в БД или Redis.
"""
import time
from collections import defaultdict, deque


class LoginThrottle:
    """Считает неудачные попытки входа по ключу (адрес клиента + логин) в скользящем окне."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300, clock=time.monotonic):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._clock = clock
        self._failures: dict[str, deque] = defaultdict(deque)

    def _prune(self, key: str) -> deque:
        """Удаляет записи, вышедшие за пределы окна, и возвращает актуальную очередь."""
        queue = self._failures[key]
        limit = self._clock() - self.window
        while queue and queue[0] <= limit:
            queue.popleft()
        return queue

    def is_blocked(self, key: str) -> bool:
        """True, если за окно накоплено максимально допустимое число неудач."""
        return len(self._prune(key)) >= self.max_attempts

    def register_failure(self, key: str) -> None:
        """Запоминает неудачную попытку."""
        self._prune(key).append(self._clock())

    def reset(self, key: str) -> None:
        """Сбрасывает счётчик после успешного входа."""
        self._failures.pop(key, None)

    def retry_after(self, key: str) -> int:
        """Сколько секунд осталось до снятия блокировки (0, если не заблокировано)."""
        queue = self._prune(key)
        if len(queue) < self.max_attempts:
            return 0
        return max(int(queue[0] + self.window - self._clock()) + 1, 1)
