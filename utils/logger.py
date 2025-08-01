"""
Настройка логирования через loguru
"""
from loguru import logger
from config.settings import settings

# Настройка форматирования и уровня логов
logger.remove()
logger.add(
    "logs/app.log",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
    rotation="1 day"
)