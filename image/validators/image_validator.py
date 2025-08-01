"""
Валидация изображений - минимальный функционал
"""
from PIL import Image
from utils.logger import logger


def validate_image(image_path):
    """
    Валидирует и загружает изображение
    Возвращает PIL Image или None при ошибке
    """
    try:
        img = Image.open(image_path)
        img.verify()  # Проверяет целостность
        img = Image.open(image_path)  # Повторно открываем после verify
        logger.info(f"Image validated: {image_path}")
        return img
    except Exception as e:
        logger.error(f"Invalid image {image_path}: {e}")
        return None