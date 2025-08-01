"""
;02=K9 D09; ?@8;>65=8O - <8=8<0;8AB8G=K9 70?CA: 1>B0
"""
import asyncio
from aiogram import Bot, Dispatcher
from config.settings import settings
from container import Container
from bot.handlers.image_handler import create_router
from utils.logger import logger
from storage.sheets_client import sheets_client


async def main():
    """0?CA: 1>B0"""
    logger.info("Starting Virtual Fitting Room Bot")
    
    # Инициализируем Google Sheets клиент
    if not await sheets_client.initialize():
        logger.warning("Failed to initialize Google Sheets client, user data won't be saved")
    
    # =8F80;870F8O 1>B0 8 48A?5BG5@0
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    # >4:;NG05< @>CB5@K
    container = Container()
    router = create_router(container)
    dp.include_router(router)
    bot.container = container
    
    # 0?CA: 1>B0
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())