#!/bin/bash

# Скрипт для быстрого деплоя на сервер

echo "🚀 Деплой Virtual Fitting Room Bot"

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с необходимыми переменными окружения"
    exit 1
fi

# Проверяем наличие Google credentials
if [ ! -f "credential-google-sheets.json" ]; then
    echo "❌ Файл credential-google-sheets.json не найден!"
    echo "Добавьте файл с Google Sheets credentials"
    exit 1
fi

# Останавливаем старый контейнер (если есть)
echo "🛑 Остановка старого контейнера..."
docker-compose down

# Собираем новый образ
echo "🔨 Сборка нового образа..."
docker-compose build --no-cache

# Запускаем контейнер
echo "▶️ Запуск контейнера..."
docker-compose up -d

# Проверяем статус
echo "📊 Статус контейнера:"
docker-compose ps

# Показываем логи
echo "📝 Логи (Ctrl+C для выхода):"
docker-compose logs -f