# Используем официальный образ Python как основу
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY ./src /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir flask requests pytest

# Задаем команду для запуска приложения
CMD ["python", "main.py"]
