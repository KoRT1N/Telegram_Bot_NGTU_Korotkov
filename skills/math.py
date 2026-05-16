import re
from skills.base import BaseSkill

class MathSkill(BaseSkill):
    """Навык выполнения математических операций"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        # Сложение
        match = re.search(r'(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)', text)
        if match:
            try:
                a = float(match.group(1))
                b = float(match.group(2))
                return f"🧮 Результат: {a} + {b} = {a + b}"
            except:
                pass
        
        # Вычитание
        match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', text)
        if match:
            try:
                a = float(match.group(1))
                b = float(match.group(2))
                return f"🧮 Результат: {a} - {b} = {a - b}"
            except:
                pass
        
        # Умножение
        match = re.search(r'(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)', text)
        if match:
            try:
                a = float(match.group(1))
                b = float(match.group(2))
                return f"🧮 Результат: {a} * {b} = {a * b}"
            except:
                pass
        
        # Деление
        match = re.search(r'(\d+\.?\d*)\s*/\s*(\d+\.?\d*)', text)
        if match:
            try:
                a = float(match.group(1))
                b = float(match.group(2))
                if b == 0:
                    return "Ошибка: деление на ноль!"
                return f"🧮 Результат: {a} / {b} = {a / b}"
            except:
                pass
        
        return "Не могу распознать математическое выражение."