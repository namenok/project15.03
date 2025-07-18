FROM python:3.12.3-slim

WORKDIR /app

# Системні залежності (для moviepy, ffmpeg тощо)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Оновлення pip і встановлення бібліотек
RUN pip install --upgrade pip setuptools wheel

# Копіюємо requirements.txt і встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Копіюємо код проєкту
COPY . .

# Запускаємо сервер
CMD ["uvicorn", "websiteProject.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
