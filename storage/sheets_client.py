"""
Клиент для работы с Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from typing import Optional, Dict, Any
from datetime import datetime

from utils.logger import logger
from config.settings import settings


class SheetsClient:
    """Клиент для работы с Google Sheets"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None
        # Для аналитики
        self.analytics_sheet = None
        self.analytics_worksheet = None
        
    async def initialize(self) -> bool:
        """Инициализация клиента Google Sheets"""
        try:
            # Загрузка учетных данных из JSON файла
            if hasattr(settings, 'google_credentials_file'):
                self.gc = gspread.service_account(filename=settings.google_credentials_file)
            else:
                logger.error("Google credentials file not specified in settings")
                return False
                
            # Открытие таблицы пользователей по ID
            self.sheet = self.gc.open_by_key(settings.users_sheet_id)
            self.worksheet = self.sheet.sheet1  # Первый лист
            
            # Открытие таблицы аналитики по ID
            self.analytics_sheet = self.gc.open_by_key(settings.analytics_sheet_id)
            self.analytics_worksheet = self.analytics_sheet.sheet1  # Первый лист
            
            logger.info("Google Sheets client initialized successfully (users + analytics)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            return False
    
    async def add_or_update_user(self, user_id: int, username: Optional[str] = None, 
                                first_name: Optional[str] = None, last_name: Optional[str] = None) -> bool:
        """
        Добавляет нового пользователя или обновляет существующего
        
        Args:
            user_id: ID пользователя в Telegram
            username: Username пользователя (может быть None)
            first_name: Имя пользователя
            last_name: Фамилия пользователя
        """
        if not self.worksheet:
            logger.error("Worksheet not initialized")
            return False
            
        try:
            # Используем find() для поиска ячейки с ID пользователя
            existing_cell = None
            try:
                existing_cell = self.worksheet.find(str(user_id))
            except gspread.CellNotFound:
                # Пользователь не найден - это нормально для новых пользователей
                pass
                
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            user_data = [
                str(user_id),
                username or "",
                first_name or "",
                last_name or "",
                current_time  # last_activity
            ]
            
            if existing_cell and existing_cell.col == 1:  # Найден в первом столбце (ID)
                # Обновляем существующего пользователя (БЕЗ токенов - они не меняются)
                row_num = existing_cell.row
                
                # Обновляем только A-E, не трогаем столбец F (tokens)
                cell_range = f"A{row_num}:E{row_num}"
                self.worksheet.update(cell_range, [user_data])
                
                logger.info(f"Updated user {user_id} in row {row_num}")
            else:
                # Добавляем нового пользователя с начальными токенами
                user_data_with_tokens = user_data + [10]  # Добавляем токены в столбец F
                self.worksheet.append_row(user_data_with_tokens)
                logger.info(f"Added new user {user_id} with 10 tokens")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to add/update user {user_id}: {e}")
            return False
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Получает статистику пользователей"""
        try:
            if not self.worksheet:
                return {"error": "Worksheet not initialized"}
                
            # Получаем количество строк с данными
            total_rows = len(self.worksheet.get_all_values()) - 1  # -1 для заголовка
            
            # Получаем колонку с username для подсчета заполненных
            username_column = self.worksheet.col_values(2)[1:]  # Пропускаем заголовок
            users_with_username = sum(1 for username in username_column if username.strip())
            
            return {
                "total_users": total_rows,
                "users_with_username": users_with_username,
                "users_without_username": total_rows - users_with_username
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {"error": str(e)}
    
    async def get_next_analytics_id(self) -> int:
        """Получает следующий ID для записи в аналитику"""
        try:
            if not self.analytics_worksheet:
                logger.error("Analytics worksheet not initialized")
                return 1
                
            # Получаем количество строк с данными (не считая заголовок)
            all_values = self.analytics_worksheet.get_all_values()
            
            # Если таблица пустая или только заголовок
            if len(all_values) <= 1:
                return 1
                
            # Возвращаем количество строк (следующий ID)
            return len(all_values)
            
        except Exception as e:
            logger.error(f"Failed to get next analytics ID: {e}")
            return 1
    
    async def log_generation(self, user_id: int, person_url: str, garment_url: str, 
                           result_url: str) -> bool:
        """
        Записывает данные о генерации в таблицу аналитики
        
        Args:
            user_id: ID пользователя в Telegram
            person_url: URL фото человека
            garment_url: URL фото одежды
            result_url: URL результата генерации
            
        Returns:
            True если успешно, False при ошибке
        """
        try:
            if not self.analytics_worksheet:
                logger.error("Analytics worksheet not initialized")
                return False
                
            # Получаем следующий ID
            next_id = await self.get_next_analytics_id()
            
            # Текущее время
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Находим первую пустую строку
            all_values = self.analytics_worksheet.get_all_values()
            next_row = len(all_values) + 1
            
            # Данные для записи в конкретные ячейки
            analytics_data = [
                next_id,           # A: id
                user_id,           # B: id_user
                person_url,        # C: input_human_image_url
                garment_url,       # D: input_garment_image_url
                result_url,        # E: output_image_url
                timestamp          # F: timestamp
            ]
            
            # Записываем данные в конкретный диапазон A:F
            cell_range = f"A{next_row}:F{next_row}"
            self.analytics_worksheet.update(cell_range, [analytics_data])
            
            logger.info(f"Logged generation for user {user_id} with ID {next_id} in row {next_row}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log generation for user {user_id}: {e}")
            return False


# Глобальный экземпляр клиента
sheets_client = SheetsClient()