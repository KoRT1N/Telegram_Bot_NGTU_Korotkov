from datetime import datetime
from skills.base import BaseSkill

class TimeSkill(BaseSkill):
    """Навык показа текущего времени"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        now = datetime.now().strftime("%H:%M")
        return f"⏰ Сейчас {now}."