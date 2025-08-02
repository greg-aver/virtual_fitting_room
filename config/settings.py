"""
Конфигурация приложения
Все настройки загружаются из файла .env
"""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
# Пытаемся найти .env в текущей директории или в родительской
import pathlib
env_path = pathlib.Path('.env')
if not env_path.exists():
    env_path = pathlib.Path('../.env')
load_dotenv(env_path)


class Settings:
    """Настройки приложения из переменных окружения"""
    
    def __init__(self):
        # Telegram Bot
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")
        
        # LLM API
        self.llm_api_key = os.getenv('LLM_API_KEY')
        self.llm_api_url = os.getenv('LLM_API_URL')
        self.llm_model = os.getenv('LLM_MODEL')
        
        # Google Sheets
        self.google_credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        self.users_sheet_id = os.getenv('USERS_SHEET_ID')
        self.analytics_sheet_id = os.getenv('ANALYTICS_SHEET_ID')
        
        # App Settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.temp_dir = os.getenv('TEMP_DIR', 'storage/temp')
        self.cache_dir = os.getenv('CACHE_DIR', 'storage/cache')


settings = Settings()