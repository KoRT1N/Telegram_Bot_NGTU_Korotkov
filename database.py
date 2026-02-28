import sqlite3
from datetime import datetime

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP
        )
    """)
    
    # Таблица для логирования сообщений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            bot_response TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Таблица для запросов погоды
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_user(user_id, name=None):
    """Сохранение или обновление пользователя"""
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # Проверяем, существует ли пользователь
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        # Обновляем существующего
        cursor.execute("""
            UPDATE users 
            SET last_seen = ?, name = COALESCE(?, name)
            WHERE user_id = ?
        """, (now, name, user_id))
    else:
        # Добавляем нового
        cursor.execute("""
            INSERT INTO users (user_id, name, first_seen, last_seen)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, now, now))
    
    conn.commit()
    conn.close()

def get_user(user_id):
    """Получение данных пользователя"""
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def log_to_db(user_id, user_message, bot_response):
    """Логирование сообщений в БД"""
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO chat_log (user_id, user_message, bot_response, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, user_message, bot_response, datetime.now()))
    
    conn.commit()
    conn.close()

def log_weather_query(user_id, city):
    """Логирование запросов погоды"""
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO weather_queries (user_id, city, timestamp)
        VALUES (?, ?, ?)
    """, (user_id, city, datetime.now()))
    
    conn.commit()
    conn.close()