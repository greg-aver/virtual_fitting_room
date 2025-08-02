"""
Сервис для управления токенами пользователей
"""
from typing import Optional
from utils.logger import logger


class TokenService:
    """Сервис для управления токенами пользователей"""
    
    def __init__(self, sheets_client):
        self.sheets_client = sheets_client
        self.initial_tokens = 10
        
    async def get_user_tokens(self, user_id: int) -> Optional[int]:
        """
        Получает количество токенов пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Количество токенов или None при ошибке
        """
        if not self.sheets_client.worksheet:
            logger.error("Worksheet not initialized")
            return None
            
        try:
            # Находим пользователя
            existing_cell = None
            try:
                existing_cell = self.sheets_client.worksheet.find(str(user_id))
            except Exception:
                logger.warning(f"User {user_id} not found in sheet")
                return None
                
            if existing_cell and existing_cell.col == 1:  # Найден в первом столбце (ID)
                row_num = existing_cell.row
                # Получаем значение из столбца F (tokens)
                tokens_cell = self.sheets_client.worksheet.cell(row_num, 6)  # 6 = столбец F
                
                try:
                    # Если ячейка пустая или None, это старый пользователь - даем ему 10 токенов
                    if tokens_cell.value is None or tokens_cell.value == "":
                        logger.info(f"User {user_id} has empty tokens field, setting to 10")
                        # Устанавливаем токены для старых пользователей
                        self.sheets_client.worksheet.update_cell(row_num, 6, 10)
                        return 10
                    
                    tokens = int(tokens_cell.value)
                    logger.info(f"User {user_id} has {tokens} tokens")
                    return tokens
                except ValueError:
                    logger.error(f"Invalid tokens value for user {user_id}: {tokens_cell.value}")
                    # Для некорректных значений тоже ставим 10
                    self.sheets_client.worksheet.update_cell(row_num, 6, 10)
                    return 10
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tokens for user {user_id}: {e}")
            return None
    
    async def decrease_tokens(self, user_id: int) -> bool:
        """
        Уменьшает токены пользователя на 1
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            True если успешно, False при ошибке
        """
        if not self.sheets_client.worksheet:
            logger.error("Worksheet not initialized")
            return False
            
        try:
            # Находим пользователя
            existing_cell = None
            try:
                existing_cell = self.sheets_client.worksheet.find(str(user_id))
            except Exception:
                logger.error(f"User {user_id} not found when trying to decrease tokens")
                return False
                
            if existing_cell and existing_cell.col == 1:  # Найден в первом столбце (ID)
                row_num = existing_cell.row
                
                # Получаем текущее количество токенов
                tokens_cell = self.sheets_client.worksheet.cell(row_num, 6)  # 6 = столбец F
                
                try:
                    current_tokens = int(tokens_cell.value or 0)
                    
                    if current_tokens <= 0:
                        logger.warning(f"User {user_id} has no tokens to decrease")
                        return False
                    
                    # Уменьшаем на 1
                    new_tokens = current_tokens - 1
                    self.sheets_client.worksheet.update_cell(row_num, 6, new_tokens)
                    
                    logger.info(f"Decreased tokens for user {user_id}: {current_tokens} -> {new_tokens}")
                    return True
                    
                except ValueError:
                    logger.error(f"Invalid tokens value for user {user_id}: {tokens_cell.value}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to decrease tokens for user {user_id}: {e}")
            return False
    
    async def has_tokens(self, user_id: int) -> bool:
        """
        Проверяет, есть ли у пользователя токены для генерации
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            True если токены есть, False если нет
        """
        tokens = await self.get_user_tokens(user_id)
        if tokens is None:
            return False
        return tokens > 0
    
    async def get_tokens_message(self, user_id: int) -> str:
        """
        Возвращает сообщение о количестве токенов пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Сообщение о токенах
        """
        tokens = await self.get_user_tokens(user_id)
        if tokens is None:
            return "Αδυναμία λήψης πληροφοριών για τα tokens"
        
        if tokens == 0:
            return "❌ Τα tokens σας εξαντλήθηκαν για τη δημιουργία εικόνων!"
        
        return f"🎟️ Εσείς έχετε ακόμη tokens: {tokens}"