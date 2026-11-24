"""Тесты ограничения числа неудачных попыток входа."""
from app.throttle import LoginThrottle


class FakeClock:
    """Управляемые «часы» для проверки скользящего окна без реального ожидания."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_blocks_after_limit():
    """После заданного числа неудач ключ блокируется, остальные ключи не затрагиваются."""
    throttle = LoginThrottle(max_attempts=3, window_seconds=60, clock=FakeClock())
    for _ in range(2):
        throttle.register_failure("a")
    assert not throttle.is_blocked("a")
    throttle.register_failure("a")
    assert throttle.is_blocked("a")
    assert not throttle.is_blocked("b")


def test_window_expires():
    """Блокировка снимается, когда неудачные попытки выходят за пределы окна."""
    clock = FakeClock()
    throttle = LoginThrottle(max_attempts=2, window_seconds=60, clock=clock)
    throttle.register_failure("a")
    throttle.register_failure("a")
    assert throttle.is_blocked("a")
    assert 0 < throttle.retry_after("a") <= 61
    clock.now += 61
    assert not throttle.is_blocked("a")
    assert throttle.retry_after("a") == 0


def test_reset_clears_counter():
    """Успешный вход обнуляет счётчик."""
    throttle = LoginThrottle(max_attempts=2, window_seconds=60, clock=FakeClock())
    throttle.register_failure("a")
    throttle.reset("a")
    throttle.register_failure("a")
    assert not throttle.is_blocked("a")
