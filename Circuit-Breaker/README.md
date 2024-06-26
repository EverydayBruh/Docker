# Реализация Паттерна "Circuit Breaker"
**Студент:** Журбенко Василий, **Группа:** Б21-525. **Год:** 2024

---

## Введение

Проект включает в себя разработку и контейнеризацию приложения, использующего паттерн "Circuit Breaker" для обработки временных сбоев при вызове внешних сервисов. Целью проекта является демонстрация эффективности паттерна "Circuit Breaker" в предотвращении распространения сбоев и повышении устойчивости приложения к временным проблемам во внешних сервисах.

## Архитектура Проекта

- **Circuit Breaker**: Компонент, реализующий логику паттерна "Circuit Breaker", обеспечивающий переключение между состояниями (CLOSED, OPEN, HALF-OPEN) и контроль за вызовами к внешнему сервису.

- **Основное Приложение**: Flask-приложение, демонстрирующее использование "Circuit Breaker" при вызове внешнего сервиса.

- **Внешний Сервис**: Заглушка на Flask, эмулирующая поведение внешнего сервиса для тестирования паттерна "Circuit Breaker".

## Результаты

- Разработана библиотека на Python для паттерна "Circuit Breaker", успешно управляющая состояниями соединения и предотвращающая повторные попытки вызова нестабильного внешнего сервиса.

- Проведено успешное модульное тестирование компонента "Circuit Breaker" с использованием `pytest`, подтверждающее его корректную работу.

- Реализованы Dockerfile и docker-compose.yml для контейнеризации основного приложения и внешнего сервиса, обеспечивая легкость в развертывании и тестировании приложения.

- Вместо реализации полноценного внешнего сервиса была использована заглушка на Flask.