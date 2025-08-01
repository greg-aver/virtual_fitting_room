from llm.clients.fal_client import FalClient
from storage.sheets_client import SheetsClient
from services.token_service import TokenService
from services.analytics_service import AnalyticsService

class Container:
    def __init__(self):
        # Создаем сервисы в правильном порядке (sheets_client первым)
        self.sheets_client = SheetsClient()
        
        # TokenService зависит от sheets_client
        self.token_service = TokenService(self.sheets_client)
        
        # Остальные независимые сервисы
        self.fal_client = FalClient()
        self.analytics_service = AnalyticsService()
