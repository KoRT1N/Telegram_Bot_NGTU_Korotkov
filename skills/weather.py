from skills.base import BaseSkill
from weather_api import handle_weather_dialog
from dialog_manager import dialog_manager

class WeatherSkill(BaseSkill):
    """Навык получения погоды"""
    
    def execute(self, text: str, user_id: int = None, match=None) -> str:
        return handle_weather_dialog(user_id, text)