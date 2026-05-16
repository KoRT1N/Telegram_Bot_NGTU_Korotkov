import random
from skills.base import BaseSkill

class SmallTalkSkill(BaseSkill):
    """Навык поддержки разговора"""
    
    RESPONSES = [
        "У меня всё отлично! А у вас?",
        "Всё хорошо, спасибо! Как ваши дела?",
        "Отлично, работаю! Что у вас нового?",
        "Нормально, помогаю пользователям. А у вас как?"
    ]
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        return random.choice(self.RESPONSES)