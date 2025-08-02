# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Проект: Virtual Fitting Room Bot

Это Telegram-бот для виртуальной примерки одежды, использующий LLM для анализа изображений.

## Команды для разработки

### Запуск проекта
```bash
python main.py
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Переменные окружения
Создайте файл `.env` со следующими переменными:
```
BOT_TOKEN=your_telegram_bot_token
LLM_API_KEY=your_llm_api_key
LLM_API_URL=your_llm_api_url
LLM_MODEL=your_model_name
GOOGLE_CREDENTIALS_FILE=credential-google-sheets.json
USERS_SHEET_ID=your_users_sheet_id
ANALYTICS_SHEET_ID=your_analytics_sheet_id
LOG_LEVEL=INFO
TEMP_DIR=storage/temp
CACHE_DIR=storage/cache
```

## Архитектура проекта

### Основные компоненты:

1. **Bot Layer** (`bot/`) - Telegram бот интерфейс
   - `handlers/image_handler.py` - обработка сообщений и изображений
   - Использует aiogram 3.x с FSM для управления состояниями

2. **LLM Integration** (`llm/`)
   - `clients/fal_client.py` - клиент для FAL API
   - `prompts/default_prompts.py` - шаблоны промптов

3. **Image Processing** (`image/`)
   - `validators/image_validator.py` - валидация загружаемых изображений

4. **Storage** (`storage/`)
   - `sheets_client.py` - интеграция с Google Sheets
   - `temp/` - временные файлы изображений
   - `cache/` - кэш данных

5. **Services** (`services/`)
   - `token_service.py` - управление токенами пользователей
   - `analytics_service.py` - сбор и анализ метрик

6. **Configuration** (`config/`)
   - `settings.py` - настройки из переменных окружения

7. **Container** (`container.py`) - DI контейнер для сервисов

### Поток работы:
1. Пользователь отправляет первое изображение (человек)
2. Бот переходит в состояние ожидания второго изображения
3. Пользователь отправляет второе изображение (одежда)
4. Бот переходит в состояние ожидания текстового промпта
5. Пользователь отправляет описание желаемого анализа
6. Бот отправляет данные в LLM API и возвращает результат

### FSM состояния:
- `waiting_first_image` - ожидание первого изображения
- `waiting_second_image` - ожидание второго изображения  
- `waiting_prompt` - ожидание текстового промпта

### Технологический стек:
- **aiogram 3.4.1** - асинхронная библиотека для Telegram Bot API
- **aiohttp 3.9.3** - HTTP клиент для LLM API запросов
- **Pillow 10.2.0** - обработка и валидация изображений
- **fal-client** - клиент для FAL API (генерация изображений)
- **gspread** - интеграция с Google Sheets
- **loguru** - продвинутое логирование
- **pydantic** - валидация конфигурации

### Особенности разработки:
- Все I/O операции асинхронные (async/await)
- Централизованное логирование через loguru в `logs/`
- Обработка ошибок на каждом уровне архитектуры
- Dependency Injection через Container класс
- Валидация данных через pydantic
- Временные файлы автоматически управляются в `storage/temp/`

### Важные файлы:
- `main.py` - точка входа в приложение
- `container.py` - контейнер зависимостей
- `bot/handlers/image_handler.py` - основная логика бота
- `config/settings.py` - конфигурация приложения
- `utils/logger.py` - настройка логирования

Проект следует принципам чистой архитектуры с четким разделением ответственности между слоями.