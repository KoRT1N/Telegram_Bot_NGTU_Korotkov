import requests
import os
from dotenv import load_dotenv
from nlp_parser import extract_city_from_text, detect_intent, process_message
from dialog_manager import dialog_manager, DialogState

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):
    """Получение погоды для указанного города"""
    
    print(f"Запрашиваю погоду для города: {city}")
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]
        
        return (f"Погода в городе {city}:\n"
                f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                f"☁️ {description}\n"
                f"💨 Ветер: {wind_speed} м/с\n"
                f"💧 Влажность: {humidity}%")
                
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return f"Город '{city}' не найден. Попробуйте уточнить название."
        return f"Ошибка API: {str(e)}"
    except requests.RequestException as e:
        return f"Ошибка соединения: {str(e)}"
    except KeyError as e:
        return f"Ошибка обработки данных: {str(e)}"

def handle_weather_dialog(user_id, message):
    """Обработка диалога о погоде с использованием FSM"""
    
    # Получаем текущее состояние пользователя
    state = dialog_manager.get_state(user_id)
    
    print(f"Состояние пользователя {user_id}: {state.value}")
    
    # Состояние START - начало диалога
    if state == DialogState.START:
        intent = detect_intent(message)
        
        # Если пользователь спрашивает погоду
        if intent == 'weather':
            # Проверяем, есть ли город в сообщении
            city = extract_city_from_text(message)
            
            if city:
                # Город есть - сразу показываем погоду
                dialog_manager.reset_user(user_id)  # сбрасываем состояние
                return get_weather(city)
            else:
                # Города нет - переходим в состояние ожидания города
                dialog_manager.set_state(user_id, DialogState.WAIT_CITY)
                return "В каком городе вас интересует погода?"
        
        return None  # Не наше намерение
    
    # Состояние WAIT_CITY - ожидаем город
    elif state == DialogState.WAIT_CITY:
        # Пытаемся извлечь город из сообщения
        city = extract_city_from_text(message)
        
        if city:
            # Город получен - показываем погоду и сбрасываем состояние
            dialog_manager.reset_user(user_id)
            return get_weather(city)
        else:
            # Не смогли определить город - просим уточнить
            return "Я не понял название города. Пожалуйста, укажите город еще раз."
    
    return None  # Не наше состояние


def handle_message(text):
    """Обрабатывает сообщение и возвращает ответ"""
    result = process_message(text)
    
    if result['type'] == 'weather':
        return get_weather(result['city'])
    else:
        return None  # None значит "не мое, пусть другие обработчики пробуют"