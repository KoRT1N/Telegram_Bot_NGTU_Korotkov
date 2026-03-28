import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from nlp_parser import extract_city_from_text, extract_days, detect_intent_hybrid
from dialog_manager import dialog_manager, DialogState

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):
    """Получение текущей погоды"""
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
        
        return (f"🌍 Погода в городе {city} сейчас:\n"
                f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                f"☁️ {description}\n"
                f"💨 Ветер: {wind_speed} м/с\n"
                f"💧 Влажность: {humidity}%")
                
    except Exception as e:
        return f"Ошибка получения данных: {str(e)}"

def get_forecast(city, days=1):
    """Получение прогноза на несколько дней"""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru",
        "cnt": min(days * 8, 40)
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        forecasts = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%d.%m')
            if date not in forecasts:
                forecasts[date] = {
                    'temps': [],
                    'descriptions': [],
                    'date_obj': datetime.fromtimestamp(item['dt'])
                }
            
            forecasts[date]['temps'].append(item['main']['temp'])
            forecasts[date]['descriptions'].append(item['weather'][0]['description'])
        
        result = f" Прогноз для {city} на {days} дн:\n\n"
        
        sorted_dates = sorted(forecasts.keys(), key=lambda x: forecasts[x]['date_obj'])
        
        for i, date in enumerate(sorted_dates[:days]):
            day_data = forecasts[date]
            avg_temp = sum(day_data['temps']) / len(day_data['temps'])
            main_desc = max(set(day_data['descriptions']), key=day_data['descriptions'].count)
            
            weekday = day_data['date_obj'].strftime('%A')
            weekday_ru = {
                'Monday': 'Пн', 'Tuesday': 'Вт', 'Wednesday': 'Ср',
                'Thursday': 'Чт', 'Friday': 'Пт', 'Saturday': 'Сб',
                'Sunday': 'Вс'
            }.get(weekday, weekday)
            
            result += f" {date} ({weekday_ru}): {avg_temp:.0f}°C, {main_desc}\n"
        
        return result
                
    except Exception as e:
        return f"Ошибка прогноза: {str(e)}"

def handle_weather_dialog(user_id, message):
    """Обработка диалога с использованием ML"""
    
    state = dialog_manager.get_state(user_id)
    
    if state == DialogState.START:
        # Используем ML для определения намерения
        intent = detect_intent_hybrid(message)
        days = extract_days(message)
        city = extract_city_from_text(message)
        
        print(f"Определен intent: {intent}, city: {city}, days: {days}")
        
        # Обработка разных интентов
        if intent == 'weather':
            if city and days is not None:
                dialog_manager.reset_user(user_id)
                return get_forecast(city, days)
            elif city:
                dialog_manager.reset_user(user_id)
                return get_weather(city)
            elif days is not None:
                dialog_manager.set_user_data(user_id, 'days', days)
                dialog_manager.set_state(user_id, DialogState.WAIT_CITY)
                return f"В каком городе узнать прогноз на {days} дн?"
            else:
                dialog_manager.set_state(user_id, DialogState.WAIT_CITY)
                return "В каком городе вас интересует погода?"
        
        return None
    
    elif state == DialogState.WAIT_CITY:
        city = extract_city_from_text(message)
        days = dialog_manager.get_user_data(user_id, 'days')
        
        if city:
            if days:
                dialog_manager.reset_user(user_id)
                return get_forecast(city, days)
            else:
                new_days = extract_days(message)
                if new_days:
                    dialog_manager.reset_user(user_id)
                    return get_forecast(city, new_days)
                else:
                    dialog_manager.reset_user(user_id)
                    return get_weather(city)
        else:
            return "Не понял город. Пожалуйста, укажите город."
    
    return None