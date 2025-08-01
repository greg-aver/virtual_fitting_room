# API Документация

## Модули и функции

### config.settings

**Класс Settings**
- Загружает конфигурацию из переменных окружения
- Валидирует параметры через Pydantic
- Основные параметры:
  - `bot_token`: токен Telegram бота
  - `llm_api_key`: ключ API для LLM
  - `llm_api_url`: URL API для fal-ai (https://fal.run/fal-ai/fashn/tryon/v1.5)
  - `llm_model`: модель виртуальной примерки (fal-ai/fashn/tryon/v1.5)

### utils.logger

**Функция настройки логирования**
- Использует библиотеку loguru
- Логи сохраняются в файл `logs/app.log`
- Ротация логов каждый день
- Уровень логирования настраивается через `LOG_LEVEL`

### image.validators.image_validator

**validate_image(image_path: str) -> Optional[Image.Image]**
- Валидирует изображение по пути
- Проверяет целостность файла
- Возвращает PIL Image объект или None при ошибке

### llm.clients.fal_client

**Класс FalClient**

**virtual_tryon(person_image_path: str, garment_image_path: str) -> Optional[str]**
- Выполняет виртуальную примерку одежды через fal-ai API
- Загружает изображения через fal_client.upload_file()
- Использует модель fal-ai/fashn/tryon/v1.5
- Возвращает URL результирующего изображения или None при ошибке

**Параметры запроса:**
- `model_image`: изображение человека
- `garment_image`: изображение одежды
- `category`: категория одежды (auto)
- `mode`: режим обработки (quality)
- `output_format`: формат вывода (png)

### bot.handlers.image_handler

**Состояния FSM:**
- `waiting_first_image`: ожидание фото человека
- `waiting_second_image`: ожидание фото одежды

**handle_photo(message: Message, state: FSMContext)**
- Обрабатывает получение фотографий
- Сохраняет и валидирует изображения
- После получения второго фото автоматически запускает виртуальную примерку
- Возвращает URL результирующего изображения

**start_handler(message: Message, state: FSMContext)**
- Обработчик команды /start
- Инициализирует процесс получения изображений

**save_photo(message: Message) -> str**
- Сохраняет фото из Telegram сообщения
- Создает временный файл в `storage/temp/`
- Возвращает путь к сохраненному файлу