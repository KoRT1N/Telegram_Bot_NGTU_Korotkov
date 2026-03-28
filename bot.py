import os
import re
import string
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()

import patterns
import weather_api
import database
from logger import log_message
from dialog_manager import dialog_manager
from weather_api import handle_weather_dialog

class ChatBot:
    def __init__(self):
        self.user_name = None
        self.current_user_id = None
        self.user_names = {}
        self.patterns = []
        self._register_patterns()
        database.init_db()

    def _register_patterns(self):
        self.patterns.extend([
            (patterns.GREETING, self.handle_greeting),
            (patterns.FAREWELL, self.handle_farewell),
            (patterns.SET_NAME, self.handle_set_name),
            (patterns.ADDITION, self.handle_addition),
            (patterns.SUBTRACTION, self.handle_subtraction),
            (patterns.MULTIPLICATION, self.handle_multiplication),
            (patterns.DIVISION, self.handle_division),
            (patterns.TIME_QUERY, self.handle_time),
            (patterns.HOW_ARE_YOU, self.handle_how_are_you),
        ])

    def preprocess_message(self, text: str) -> str:
        text = text.lower().strip()
        return text

    def process(self, message: str, user_id: int = None) -> str:
        """Основной метод: принимает строку, возвращает ответ бота."""
        original = message
        cleaned = self.preprocess_message(message)
        
        if user_id:
            self.current_user_id = user_id
            # Загружаем имя пользователя из БД
            db_name = database.get_user(user_id)
            if db_name:
                self.user_names[user_id] = db_name
            self.user_name = self.user_names.get(user_id)
            
            # Сохраняем/обновляем пользователя
            database.save_user(user_id, self.user_name)
        
        # ===== НОВОЕ: Обработка через Dialog Manager =====
        # Сначала проверяем, есть ли активный диалог
        state = dialog_manager.get_state(user_id) if user_id else None
        
        if state and state.value != "start":
            # Если есть активный диалог, обрабатываем через соответствующий обработчик
            weather_response = handle_weather_dialog(user_id, original)
            if weather_response:
                if user_id:
                    database.log_to_db(user_id, original, weather_response)
                log_message(original, weather_response)
                return weather_response
        
        # Если нет активного диалога, пробуем обычные обработчики
        # Проверяем, не спрашивают ли погоду (но без активного диалога)
        weather_response = handle_weather_dialog(user_id, original)
        if weather_response:
            if user_id:
                database.log_to_db(user_id, original, weather_response)
            log_message(original, weather_response)
            return weather_response
        
        # Если не погода, проверяем остальные шаблоны
        for pattern, handler in self.patterns:
            match = pattern.search(cleaned)
            if match:
                response = handler(match)
                if user_id:
                    database.log_to_db(user_id, original, response)
                log_message(original, response)
                return response
        
        # Если ни один шаблон не подошёл
        response = "Извините, я не понимаю ваш запрос."
        if user_id:
            database.log_to_db(user_id, original, response)
        log_message(original, response)
        return response

    # ----- Обработчики (без изменений) -----
    def handle_greeting(self, match):
        user_name = self.user_names.get(self.current_user_id) if self.current_user_id else None
        if user_name:
            return f"Здравствуйте, {user_name}! Чем могу помочь?"
        return "Здравствуйте! Чем могу помочь?"

    def handle_farewell(self, match):
        return "До свидания! Было приятно пообщаться."

    def handle_set_name(self, match):
        name = match.group(1).capitalize()
        if self.current_user_id:
            self.user_names[self.current_user_id] = name
            database.save_user(self.current_user_id, name)
            self.user_name = name
        return f"Приятно познакомиться, {name}!"

    def handle_addition(self, match):
        try:
            a = float(match.group(1))
            b = float(match.group(2))
            return f"Результат сложения: {a} + {b} = {a + b}"
        except ValueError:
            return "Не могу распознать числа для сложения."

    def handle_subtraction(self, match):
        try:
            a = float(match.group(1))
            b = float(match.group(2))
            return f"Результат вычитания: {a} - {b} = {a - b}"
        except ValueError:
            return "Не могу распознать числа для вычитания."

    def handle_multiplication(self, match):
        try:
            a = float(match.group(1))
            b = float(match.group(2))
            return f"Результат умножения: {a} * {b} = {a * b}"
        except ValueError:
            return "Не могу распознать числа для умножения."

    def handle_division(self, match):
        try:
            a = float(match.group(1))
            b = float(match.group(2))
            if b == 0:
                return "Ошибка: деление на ноль!"
            return f"Результат деления: {a} / {b} = {a / b}"
        except ValueError:
            return "Не могу распознать числа для деления."

    def handle_time(self, match):
        now = datetime.now().strftime("%H:%M")
        return f"Сейчас {now}."

    def handle_how_are_you(self, match):
        return "У меня всё отлично! А у вас?"

# --- Telegram часть ---
chat_bot = ChatBot()

async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    bot_response = chat_bot.process(user_message, user_id)
    await update.message.reply_text(bot_response)

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ОШИБКА: Не найден токен!")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler))
    
    print("✅ Бот запущен с поддержкой FSM диалогов!")
    print("Ожидание сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()