# Используем официальный Python 3.12.3 образ
FROM python:3.12.3-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для обработки изображений
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем необходимые директории
RUN mkdir -p logs storage/temp storage/cache

# Устанавливаем права на директории
RUN chmod -R 755 storage logs

# Создаем пользователя для запуска приложения (безопасность)
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Команда для запуска
CMD ["python", "main.py"]