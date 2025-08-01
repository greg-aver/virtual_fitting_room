"""
Обработчик изображений для Telegram бота - минималистичная реализация
"""
import os
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from llm.clients.fal_client import FalClient
from image.validators.image_validator import validate_image
from config.settings import settings
from utils.logger import logger
from storage.sheets_client import sheets_client
from services.token_service import token_service
from services.analytics_service import analytics_service

from bot.text import MESSAGES, PROMPTS


async def send_typing_periodically(bot, chat_id: int, duration: int = 30):
    """Отправляет typing action каждые 5 секунд"""
    for _ in range(duration // 5):
        await bot.send_chat_action(chat_id=chat_id, action="typing")
        await asyncio.sleep(5)

router = Router()
llm_client = FalClient()


class ImageProcessing(StatesGroup):
    """Состояния для обработки изображений"""
    waiting_first_image = State()
    waiting_second_image = State()


@router.message(F.content_type == "photo")
async def handle_photo(message: Message, state: FSMContext):
    """Обрабатывает получение фотографий"""
    current_state = await state.get_state()
    
    # Сохраняем фото
    photo_path = await save_photo(message)
    if not photo_path:
        await message.answer("Ошибка сохранения фото")
        return
    
    # Валидируем изображение
    if not validate_image(photo_path):
        await message.answer("Некорректное изображение")
        return
    
    if current_state == ImageProcessing.waiting_first_image:
        await state.update_data(human_image=photo_path)
        await state.set_state(ImageProcessing.waiting_second_image)
        await message.answer("Фото получено! Теперь пришлите фото одежды")
        
    elif current_state == ImageProcessing.waiting_second_image:
        await state.update_data(garment_image=photo_path)
        
        # Проверяем токены перед генерацией
        user_id = message.from_user.id
        if not await token_service.has_tokens(user_id):
            tokens_message = await token_service.get_tokens_message(user_id)
            await message.answer(tokens_message)
            await state.clear()
            return
        
        # Показываем индикатор печати и сообщение
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await message.answer("Обрабатываю виртуальную примерку...")
        
        # Запускаем typing в фоне
        typing_task = asyncio.create_task(
            send_typing_periodically(message.bot, message.chat.id, duration=60)
        )
        
        try:
            # Получаем данные и выполняем виртуальную примерку
            data = await state.get_data()
            result_data = await llm_client.virtual_tryon(data["human_image"], photo_path)
            
            # Останавливаем typing
            typing_task.cancel()
            
            if result_data and isinstance(result_data, dict):
                # Списываем токен только при успешной генерации
                await token_service.decrease_tokens(user_id)
                
                # Записываем аналитику
                await analytics_service.log_generation(
                    user_id=user_id,
                    person_url=result_data['person_url'],
                    garment_url=result_data['garment_url'],
                    result_url=result_data['result_url']
                )
                
                # Показываем результат и остаток токенов
                await message.answer(f"Готово! Результат виртуальной примерки: {result_data['result_url']}")
                tokens_message = await token_service.get_tokens_message(user_id)
                await message.answer(tokens_message)
                
                # Проверяем, есть ли еще токены для продолжения
                if await token_service.has_tokens(user_id):
                    await asyncio.sleep(2)  # Небольшая пауза
                    await message.answer(MESSAGES["ask_photo_person"])
                    await state.set_state(ImageProcessing.waiting_first_image)
                else:
                    # Если токенов нет, завершаем сессию полностью
                    await state.clear()
            else:
                await message.answer("Произошла ошибка при обработке изображений")
                # При ошибке показываем токены и возвращаемся к началу цикла
                tokens_message = await token_service.get_tokens_message(user_id)
                await message.answer(tokens_message)
                await asyncio.sleep(1)
                await message.answer(MESSAGES["ask_photo_person"])
                await state.set_state(ImageProcessing.waiting_first_image)
                
        except Exception as e:
            # Останавливаем typing при ошибке
            typing_task.cancel()
            logger.error(f"Error during virtual try-on: {e}")
            await message.answer("Произошла ошибка при обработке изображений")
            # При ошибке показываем токены и возвращаемся к началу цикла
            tokens_message = await token_service.get_tokens_message(user_id)
            await message.answer(tokens_message)
            await asyncio.sleep(1)
            await message.answer(MESSAGES["ask_photo_person"])
            await state.set_state(ImageProcessing.waiting_first_image)
    
    else:
        # Если пользователь отправил фото без /start
        await message.answer("Привет! Для начала работы отправьте команду /start")




@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    """Начало работы с ботом с задержкой между сообщениями"""
    # Сохраняем данные пользователя в таблицу
    user = message.from_user
    await sheets_client.add_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    await message.answer(MESSAGES["hello"])
    await asyncio.sleep(2)  # Пауза 2 секунды
    
    # Показываем количество токенов
    tokens_message = await token_service.get_tokens_message(user.id)
    await message.answer(tokens_message)
    await asyncio.sleep(1)
    
    await message.answer(MESSAGES["ask_photo_person"])
    await state.set_state(ImageProcessing.waiting_first_image)


async def save_photo(message: Message) -> str:
    """Сохраняет фото из сообщения, возвращает путь к файлу"""
    try:
        photo = message.photo[-1]  # Берем фото максимального качества
        file_info = await message.bot.get_file(photo.file_id)
        
        # Создаем путь для сохранения
        file_path = os.path.join(settings.temp_dir, f"{photo.file_id}.jpg")
        os.makedirs(settings.temp_dir, exist_ok=True)
        
        # Скачиваем файл
        await message.bot.download_file(file_info.file_path, file_path)
        
        logger.info(f"Photo saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save photo: {e}")
        return None