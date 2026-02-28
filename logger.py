from datetime import datetime

def log_message(user_message: str, bot_response: str):
    """Записывает диалог в файл с временной меткой."""
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] USER: {user_message}\n")
        f.write(f"[{datetime.now()}] BOT: {bot_response}\n")
        