import time

class CircuitBreaker:
    def __init__(self, failure_threshold, recovery_timeout, failure_count=0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = failure_count
        self.state = "CLOSED"
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        current_time = time.time()
        if self.state == "OPEN" and (current_time - self.last_failure_time) > self.recovery_timeout:
            self.state = "HALF-OPEN"

        if self.state == "OPEN":
            raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN" or self.state == "CLOSED":
                self.reset()  # Успешный вызов сбрасывает счетчик и состояние
            return result
        except Exception as e:
            self.record_failure(e)
            raise

    def reset(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self, exception):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_failure_time = time.time()
        elif self.state == "HALF-OPEN":
            # Если происходит неудача в состоянии HALF-OPEN, возвращаемся в OPEN
            self.state = "OPEN"
