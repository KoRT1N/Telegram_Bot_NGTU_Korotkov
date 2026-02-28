import os
from dotenv import load_dotenv

print("1. Текущая директория:", os.getcwd())
print("2. Содержимое .env файла:")
try:
    with open('.env', 'rb') as f:  # читаем в бинарном режиме
        content = f.read()
        print("   Байты (первые 20):", content[:20])
        print("   Как текст:", content.decode('utf-8', errors='replace')[:50])
except Exception as e:
    print("   Ошибка чтения:", e)

print("\n3. Загружаем .env...")
load_dotenv()
print("4. .env загружен")

print("5. Ищем BOT_TOKEN...")
token = os.getenv("BOT_TOKEN")
print(f"   BOT_TOKEN = {token}")

# Проверим все переменные, которые начинаются с BOT
print("\n6. Все переменные с 'BOT' в имени:")
for key, value in os.environ.items():
    if 'BOT' in key.upper():
        print(f"   {key} = {value}")