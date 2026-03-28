from enum import Enum
import database

class DialogState(Enum):
    """Состояния диалога"""
    START = "start"              # начальное состояние
    WAIT_CITY = "wait_city"      # ожидание города
    WAIT_DATE = "wait_date"      # ожидание даты (для доп. задания)

class DialogManager:
    def __init__(self):
        # Хранилище состояний пользователей {user_id: state}
        self.user_states = {}
        # Хранилище данных пользователей {user_id: {city: ..., date: ...}}
        self.user_data = {}
        
    def get_state(self, user_id):
        """Получить текущее состояние пользователя"""
        if user_id in self.user_states:
            return self.user_states[user_id]
        return DialogState.START
    
    def set_state(self, user_id, state):
        """Установить состояние пользователя"""
        self.user_states[user_id] = state
        # Инициализируем данные пользователя если нужно
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        print(f"Пользователь {user_id} перешел в состояние {state.value}")
    
    def get_user_data(self, user_id, key=None):
        """Получить данные пользователя"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        
        if key:
            return self.user_data[user_id].get(key)
        return self.user_data[user_id]
    
    def set_user_data(self, user_id, key, value):
        """Сохранить данные пользователя"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id][key] = value
        
    def clear_user_data(self, user_id):
        """Очистить данные пользователя"""
        if user_id in self.user_data:
            self.user_data[user_id] = {}
            
    def reset_user(self, user_id):
        """Сбросить состояние и данные пользователя"""
        if user_id in self.user_states:
            del self.user_states[user_id]
        if user_id in self.user_data:
            del self.user_data[user_id]

# Глобальный экземпляр менеджера диалогов
dialog_manager = DialogManager()