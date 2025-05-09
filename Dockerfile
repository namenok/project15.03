# Офіційний Python-образ
FROM python:3.12.3-slim

# Робоча директорія в контейнері
WORKDIR /app

# Копіюємо requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код
COPY . .

# Команда для запуску Django-сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]