# 🔹 Base stage
FROM python:3.12.3-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libxext6 \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

# 🔹 Dev stage
FROM base as dev

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

#  Final prod
FROM base as prod

RUN python manage.py collectstatic --noinput

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "--verbosity", "3", "websiteProject.asgi:application"]