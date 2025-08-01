"""
Клиент для работы с fal-ai API - виртуальная примерка одежды
"""
import os
from config.settings import settings
from utils.logger import logger


class FalClient:
    """Клиент для fal-ai FASHN Virtual Try-On API"""
    
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        
        # Устанавливаем переменную окружения для fal-client
        os.environ['FAL_KEY'] = self.api_key
    
    async def virtual_tryon(self, person_image_path, garment_image_path):
        """
        Выполняет виртуальную примерку одежды
        
        Args:
            person_image_path: Путь к фото человека
            garment_image_path: Путь к фото одежды
            
        Returns:
            Словарь с URL изображений или None при ошибке:
            {
                'person_url': str,
                'garment_url': str, 
                'result_url': str
            }
        """
        try:
            import fal_client
            
            logger.info(f"Starting virtual try-on with person: {person_image_path}, garment: {garment_image_path}")
            
            # Загружаем изображения
            logger.info("Uploading person image...")
            person_image_url = fal_client.upload_file(person_image_path)
            logger.info(f"Person image uploaded: {person_image_url}")
            
            logger.info("Uploading garment image...")
            garment_image_url = fal_client.upload_file(garment_image_path)
            logger.info(f"Garment image uploaded: {garment_image_url}")
            
            # Отправляем запрос на виртуальную примерку
            logger.info("Submitting virtual try-on request...")
            result = fal_client.subscribe(
                self.model,
                arguments={
                    "model_image": person_image_url,
                    "garment_image": garment_image_url,
                    "category": "auto",
                    "mode": "quality",
                    "garment_photo_type": "auto",
                    "num_samples": 1,
                    "seed": 42,
                    "output_format": "png"
                },
                with_logs=True
            )
            
            logger.info(f"Received result: {result}")
            
            # Извлекаем URL результата
            if result and "images" in result and len(result["images"]) > 0:
                result_url = result["images"][0]["url"]
                logger.info(f"Virtual try-on completed successfully: {result_url}")
                
                # Возвращаем все URL для аналитики
                return {
                    'person_url': person_image_url,
                    'garment_url': garment_image_url,
                    'result_url': result_url
                }
            else:
                logger.error(f"No images in fal-ai response. Full result: {result}")
                return None
                
        except ImportError:
            logger.error("fal-client library not installed. Run: pip install fal-client")
            return None
        except Exception as e:
            logger.error(f"Virtual try-on failed: {e}")
            return None