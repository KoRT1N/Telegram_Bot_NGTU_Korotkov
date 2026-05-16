import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from skills import (
    WeatherSkill, TimeSkill, DateSkill, GreetingSkill,
    FarewellSkill, HelpSkill, SmallTalkSkill, MathSkill, SetNameSkill
)
from nlp_parser import detect_intent_hybrid
from dialog_manager import dialog_manager
from database import init_db, log_to_db, get_user
from logger import log_message
from tts_silero import tts_engine
import logging

load_dotenv()


try:
    from tts_silero import tts_engine
    TTS_AVAILABLE = True
    print("🔊 TTS модуль загружен")
except ImportError as e:
    TTS_AVAILABLE = False
    tts_engine = None
    print(f"⚠️ TTS модуль не загружен: {e}")
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class SkillRouter:
    """Маршрутизатор запросов к навыкам"""
    
    def __init__(self, bot_instance=None):
        self.skills = {
            'weather': WeatherSkill(bot_instance),
            'time': TimeSkill(bot_instance),
            'date': DateSkill(bot_instance),
            'greeting': GreetingSkill(bot_instance),
            'farewell': FarewellSkill(bot_instance),
            'help': HelpSkill(bot_instance),
            'how_are_you': SmallTalkSkill(bot_instance),
            'addition': MathSkill(bot_instance),
            'subtraction': MathSkill(bot_instance),
            'multiplication': MathSkill(bot_instance),
            'division': MathSkill(bot_instance),
            'set_name': SetNameSkill(bot_instance),
        }
    
    def route(self, intent: str, text: str, user_id: int = None) -> str:
        """Маршрутизация запроса к соответствующему навыку"""
        if intent in self.skills:
            return self.skills[intent].execute(text, user_id)
        return None

class ChatBot:
    def __init__(self):
        self.user_name = None
        self.current_user_id = None
        self.router = SkillRouter(self)
        init_db()
    
    def process(self, message: str, user_id: int = None) -> str:
        original = message
        
        if user_id:
            self.current_user_id = user_id
            db_name = get_user(user_id)
            if db_name:
                self.user_name = db_name
        
        # Проверка активного диалога (FSM)
        state = dialog_manager.get_state(user_id) if user_id else None
        
        if state and state.value != "start":
            # Обработка через FSM (сейчас только для погоды)
            from weather_api import handle_weather_dialog
            response = handle_weather_dialog(user_id, original)
            if response:
                self._log(user_id, original, response)
                return response
        
        # Определяем intent через BERT
        intent = detect_intent_hybrid(original)
        print(f"[Intent] {intent}")
        
        # Маршрутизация к навыку
        response = self.router.route(intent, original, user_id)
        
        if response:
            self._log(user_id, original, response)
            return response
        
        # Если ничего не подошло
        response = "Извините, я не понимаю ваш запрос."
        self._log(user_id, original, response)
        return response
    
    def _log(self, user_id, user_message, bot_response):
        """Логирование сообщения"""
        if user_id:
            log_to_db(user_id, user_message, bot_response)
        log_message(user_message, bot_response)

# --- Telegram часть ---
chat_bot = ChatBot()

async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    bot_response = chat_bot.process(user_message, user_id)
    await update.message.reply_text(bot_response)
    

async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    bot_response = chat_bot.process(user_message, user_id)
    
    # Отправляем текст
    await update.message.reply_text(bot_response)
    
    # Отправляем голос (если TTS доступен)
    if TTS_AVAILABLE and tts_engine and len(bot_response) < 500:
        exclude = ["Извините, я не понимаю ваш запрос.", "Здравствуйте! Чем могу помочь?"]
        if bot_response not in exclude:
            try:
                audio_bytes = tts_engine.text_to_audio_with_cache(bot_response)
                await update.message.reply_voice(voice=audio_bytes)
            except Exception as e:
                logger.error(f"Ошибка TTS: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("ОШИБКА: Не найден токен!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler))
    
    print("✅ Бот запущен с Skill-архитектурой!")
    print("Доступные навыки: weather, time, date, greeting, farewell, help, smalltalk, math, set_name")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()