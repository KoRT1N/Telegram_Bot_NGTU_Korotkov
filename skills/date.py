from datetime import datetime
from skills.base import BaseSkill

class DateSkill(BaseSkill):
    """Навык показа текущей даты"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        now = datetime.now().strftime("%d.%m.%Y")
        return f"📅 Сегодня {now}."