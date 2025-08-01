"""
Сервис для аналитики генераций изображений
"""
from utils.logger import logger


class AnalyticsService:
    """Сервис для записи аналитики генераций"""
    
    def __init__(self, sheets_client):
        self.sheets_client = sheets_client
        
    async def log_generation(self, user_id: int, person_url: str, garment_url: str, 
                           result_url: str) -> bool:
        """
        Записывает данные о генерации в таблицу аналитики
        
        Args:
            user_id: ID пользователя в Telegram
            person_url: URL фото человека из fal.ai
            garment_url: URL фото одежды из fal.ai
            result_url: URL результата генерации
            
        Returns:
            True если успешно, False при ошибке
        """
        try:
            # Используем метод sheets_client для записи
            success = await self.sheets_client.log_generation(
                user_id=user_id,
                person_url=person_url,
                garment_url=garment_url,
                result_url=result_url
            )
            
            if success:
                logger.info(f"Analytics logged successfully for user {user_id}")
            else:
                logger.error(f"Failed to log analytics for user {user_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Analytics service error for user {user_id}: {e}")
            return False
    
    async def is_available(self) -> bool:
        """
        Проверяет, доступен ли сервис аналитики
        
        Returns:
            True если доступен, False если нет
        """
        try:
            return self.sheets_client.analytics_worksheet is not None
        except Exception as e:
            logger.error(f"Analytics availability check failed: {e}")
            return False