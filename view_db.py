import sqlite3
from datetime import datetime

def view_database():
    """Просмотр всех данных в базе SQLite"""
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    print("="*60)
    print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
    print("="*60)
    
    # 1. Таблица users
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    print(f"\n👥 Пользователи: {users_count}")
    
    if users_count > 0:
        print("\n" + "-"*40)
        cursor.execute("SELECT user_id, name, first_seen, last_seen FROM users ORDER BY last_seen DESC LIMIT 5")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user[0]}, Имя: {user[1] or 'не указано'}")
            print(f"   Первый визит: {user[2]}")
            print(f"   Последний визит: {user[3]}")
    
    # 2. Таблица chat_log
    cursor.execute("SELECT COUNT(*) FROM chat_log")
    messages_count = cursor.fetchone()[0]
    print(f"\n💬 Сообщений в логе: {messages_count}")
    
    if messages_count > 0:
        print("\n" + "-"*40)
        print("Последние 5 сообщений:")
        cursor.execute("""
            SELECT user_id, user_message, bot_response, timestamp 
            FROM chat_log 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        messages = cursor.fetchall()
        for msg in messages:
            print(f"\n[{msg[3]}]")
            print(f"👤 Пользователь {msg[0]}: {msg[1]}")
            print(f"🤖 Бот: {msg[2]}")
    
    # 3. Таблица weather_queries
    cursor.execute("SELECT COUNT(*) FROM weather_queries")
    weather_count = cursor.fetchone()[0]
    print(f"\n🌤 Запросов погоды: {weather_count}")
    
    if weather_count > 0:
        print("\n" + "-"*40)
        print("Последние запросы погоды:")
        cursor.execute("""
            SELECT user_id, city, timestamp 
            FROM weather_queries 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        weather = cursor.fetchall()
        for w in weather:
            print(f"[{w[2]}] Пользователь {w[0]} запросил: {w[1]}")
    
    conn.close()

if __name__ == "__main__":
    view_database()