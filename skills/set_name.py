import re
from skills.base import BaseSkill
from database import save_user

class SetNameSkill(BaseSkill):
    """Навык запоминания имени пользователя"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        # Ищем имя в тексте
        patterns = [
            r'меня зовут\s+([а-яА-Яa-zA-Z]+)',
            r'мое имя\s+([а-яА-Яa-zA-Z]+)',
            r'зовите меня\s+([а-яА-Яa-zA-Z]+)',
            r'я\s+([а-яА-Яa-zA-Z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                if user_id:
                    save_user(user_id, name)
                return f"Приятно познакомиться, {name}!"
        
        return None