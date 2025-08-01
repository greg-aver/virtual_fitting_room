"""
Главный файл приложения - минималистичный запуск бота
"""
import asyncio
from aiogram import Bot, Dispatcher
from config.settings import settings
from container import Container
from bot.handlers.image_handler import create_router
from utils.logger import logger


async def main():
    """Запуск бота"""
    logger.info("Starting Virtual Fitting Room Bot")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # Подключаем роутеры
    container = Container()
    
    # Инициализируем контейнер (включая sheets_client)
    await container.initialize()
    
    router = create_router(container)
    dp.include_router(router)
    bot.container = container
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())