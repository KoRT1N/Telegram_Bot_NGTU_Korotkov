from skills.base import BaseSkill
from database import get_user

class GreetingSkill(BaseSkill):
    """Навык приветствия"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        user_name = get_user(user_id) if user_id else None
        if user_name:
            return f"Здравствуйте, {user_name}! Чем могу помочь?"
        return "Здравствуйте! Чем могу помочь?"