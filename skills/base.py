from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """Базовый класс для всех навыков"""
    
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
    
    @abstractmethod
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        """Выполнение навыка"""
        pass
    
    def get_name(self) -> str:
        return self.__class__.__name__