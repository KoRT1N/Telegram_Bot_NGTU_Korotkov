from skills.base import BaseSkill

class FarewellSkill(BaseSkill):
    """Навык прощания"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        return "До свидания! Было приятно пообщаться."