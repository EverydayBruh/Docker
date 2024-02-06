import pytest
import sys
sys.path.append('/mnt/u/NewPojects/Proga/Docker/Docker/Circuit-Breaker/scr')
from circuit_breaker import CircuitBreaker
import time

# Функция для имитации успешного вызова
def mock_success(*args, **kwargs):
    return "Success"

# Функция для имитации вызова с ошибкой
def mock_failure(*args, **kwargs):
    raise Exception("Fail")

# Тестирование сброса Circuit Breaker после ошибок
def test_circuit_breaker_reset():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    with pytest.raises(Exception):
        breaker.call(mock_failure)
    with pytest.raises(Exception):
        breaker.call(mock_failure)
    assert breaker.state == "OPEN"
    time.sleep(1)
    # Проверяем, сбросился ли Circuit Breaker после таймаута
    breaker.call(mock_success)  # Должно сбросить состояние
    assert breaker.state == "CLOSED"

# Тестирование перехода в состояние HALF-OPEN и обратно в CLOSED
def test_circuit_breaker_half_open_to_closed():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
    with pytest.raises(Exception):
        breaker.call(mock_failure)
    time.sleep(1.1)  # Убедимся, что таймаут восстановления точно прошел
    # Попытка вызова после таймаута для проверки перехода в HALF-OPEN
    try:
        breaker.call(mock_success)  # Должно перевести в HALF-OPEN, затем в CLOSED после успеха
    except:
        pass  # В случае ошибки пропускаем, так как здесь нас интересует только переход состояния
    assert breaker.state == "CLOSED"
