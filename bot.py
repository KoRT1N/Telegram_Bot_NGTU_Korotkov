import re
import string
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

import asyncio

import patterns
import weather_api
import database
from logger import log_message

load_dotenv()

class ChatBot:
    def __init__(self):
        self.user_name = None
        self.current_user_id = None  # Добавляем ID текущего пользователя
        self.patterns = []
        self._register_patterns()
        database.init_db()  # Инициализируем БД при запуске

    def _register_patterns(self):
        self.patterns.extend([
            (patterns.GREETING, self.handle_greeting),
            (patterns.FAREWELL, self.handle_farewell),
            (patterns.WEATHER, self.handle_weather),
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
        """Обновленный метод с поддержкой user_id"""
        original = message
        cleaned = self.preprocess_message(message)
        
        # Сохраняем ID пользователя
        if user_id:
            self.current_user_id = user_id
            database.save_user(user_id, self.user_name)

        for pattern, handler in self.patterns:
            match = pattern.search(cleaned)
            if match:
                response = handler(match)
                # Логируем в БД
                if user_id:
                    database.log_to_db(user_id, original, response)
                # Также логируем в файл (для совместимости)
                log_message(original, response)
                return response

        response = "Извините, я не понимаю ваш запрос."
        if user_id:
            database.log_to_db(user_id, original, response)
        log_message(original, response)
        return response

    # ----- Обработчики -----
    def handle_greeting(self, match):
        if self.user_name:
            return f"Здравствуйте, {self.user_name}! Чем могу помочь?"
        return "Здравствуйте! Чем могу помочь?"

    def handle_farewell(self, match):
        return "До свидания! Было приятно пообщаться."

    def handle_weather(self, match):
        city = match.group(1).strip()
        
        # Логируем запрос погоды
        if self.current_user_id:
            database.log_weather_query(self.current_user_id, city)
        
        # Получаем реальную погоду через API
        return weather_api.get_weather(city)

    def handle_set_name(self, match):
        name = match.group(1).capitalize()
        self.user_name = name
        
        # Обновляем имя в БД
        if self.current_user_id:
            database.save_user(self.current_user_id, name)
            
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
    """Обработчик входящих сообщений от Telegram."""
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    # Отвечаем через нашего бота
    bot_response = chat_bot.process(user_message, user_id)
    await update.message.reply_text(bot_response)

def main():
    # Вставьте сюда токен
    TOKEN = os.getenv("BOT_TOKEN")
    
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчик
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()