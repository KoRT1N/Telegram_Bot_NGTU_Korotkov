import spacy
import re

# Загружаем русскую модель
try:
    nlp = spacy.load("ru_core_news_sm")
    print("✅ spaCy модель загружена")
except:
    print("Устанавливаю русскую модель...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_sm"])
    nlp = spacy.load("ru_core_news_sm")

# База городов с их корнями и вариантами написания
CITY_DATABASE = {
    # Москва
    'москв': 'Москва',  # корень для москва, москве, москвы, москвой
    'мск': 'Москва',
    
    # Санкт-Петербург
    'петербург': 'Санкт-Петербург',  # корень
    'питер': 'Санкт-Петербург',
    'питер': 'Санкт-Петербург',  # питер, питере, питера
    'ленинград': 'Санкт-Петербург',
    'спб': 'Санкт-Петербург',
    
    # Нижний Новгород
    'нижн': 'Нижний Новгород',  # для нижний, нижнего, нижнем
    'новгород': 'Нижний Новгород',  # новгород, новгороде, новгорода
    'нновгород': 'Нижний Новгород',
    'нн': 'Нижний Новгород',
    
    # Лондон
    'лондон': 'Лондон',  # лондон, лондона, лондоне, лондоном
    
    # Париж
    'париж': 'Париж',  # париж, парижа, париже
    
    # Берлин
    'берлин': 'Берлин',
    
    # Рим
    'рим': 'Рим',
    
    # Токио
    'токио': 'Токио',
    
    # Нью-Йорк
    'нью': 'Нью-Йорк',
    'йорк': 'Нью-Йорк',
    'ньюйорк': 'Нью-Йорк',
    'ny': 'New York',
    
    # Ростов-на-Дону
    'ростов': 'Ростов-на-Дону',
}

# Дополнительный словарь соответствий английских названий
ENGLISH_CITIES = {
    'london': 'Лондон',
    'moscow': 'Москва',
    'paris': 'Париж',
    'berlin': 'Берлин',
    'rome': 'Рим',
    'tokyo': 'Токио',
    'new york': 'Нью-Йорк',
    'spb': 'Санкт-Петербург',
    'peter': 'Санкт-Петербург',
}

def extract_city_root(word):
    """Извлекает корень слова (отбрасывает окончание)"""
    word = word.lower()
    
    # Список окончаний для разных падежей
    endings = [
        'а', 'у', 'е', 'и', 'ой', 'ою', 'еи', 'ей',  # русские окончания
        'ом', 'ем', 'ами', 'ях', 'ах',
        's', 'es',  # английские окончания
    ]
    
    # Пробуем отбросить каждое окончание
    for ending in endings:
        if word.endswith(ending) and len(word) > len(ending) + 2:
            root = word[:-len(ending)]
            # Проверяем, есть ли такой корень в базе
            if root in CITY_DATABASE:
                return root
    
    return word

def find_city_by_root(word):
    """Ищет город по корню слова"""
    word = word.lower().strip()
    
    # Прямой поиск в базе
    if word in CITY_DATABASE:
        return CITY_DATABASE[word]
    
    # Поиск по корню
    root = extract_city_root(word)
    if root in CITY_DATABASE:
        print(f"Найден по корню: '{word}' -> корень '{root}' -> {CITY_DATABASE[root]}")
        return CITY_DATABASE[root]
    
    # Поиск частичного совпадения (например, "лонд" в "лондоне")
    for city_root, city_name in CITY_DATABASE.items():
        if city_root in word and len(city_root) > 3:
            print(f"Найден по частичному совпадению: '{word}' похож на '{city_root}'")
            return city_name
    
    return None

def extract_city_from_text(text):
    """Извлекает город из текста запроса"""
    text_lower = text.lower()
    
    # 1. Проверяем английские названия
    for eng_name, rus_city in ENGLISH_CITIES.items():
        if eng_name in text_lower:
            print(f"Найден английский город: {eng_name} -> {rus_city}")
            return rus_city
    
    # 2. Ищем слова после предлога "в" или "во"
    import re
    match = re.search(r'[вво]\s+([а-яА-Яa-zA-Z\-]+(?:[-\s][а-яА-Яa-zA-Z\-]+)?)', text_lower)
    if match:
        potential_city = match.group(1).strip()
        print(f"Слово после предлога: '{potential_city}'")
        
        # Разбиваем на отдельные слова
        words = re.findall(r'[а-яА-Яa-zA-Z\-]+', potential_city)
        for word in words:
            found_city = find_city_by_root(word)
            if found_city:
                return found_city
    
    # 3. Ищем в тексте все возможные названия городов
    words = re.findall(r'[а-яА-Яa-zA-Z]{4,}', text_lower)  # слова длиннее 3 букв
    for word in words:
        found_city = find_city_by_root(word)
        if found_city:
            print(f"Найден город в тексте: '{word}' -> {found_city}")
            return found_city
    
    # 4. Используем spaCy как запасной вариант
    doc = nlp(text_lower)
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:
            city = ent.text
            print(f"Найден через spaCy: {city}")
            found = find_city_by_root(city)
            if found:
                return found
            return city.capitalize()
    
    return None

def is_weather_query(text):
    """Проверяет, спрашивают ли про погоду"""
    weather_keywords = [
        'погод', 'температур', 'градус', 'тепл', 'холодн', 
        'мороз', 'ветер', 'дожд', 'снег', 'солн', 'облач',
        'weather', 'temperature', 'forecast'
    ]
    text_lower = text.lower()
    
    for keyword in weather_keywords:
        if keyword in text_lower:
            return True
    return False

def process_message(text):
    """Обрабатывает сообщение и определяет, что нужно делать"""
    # Проверяем, есть ли в сообщении город
    city = extract_city_from_text(text)
    
    # Если нашли город и это похоже на вопрос о погоде
    if city and is_weather_query(text):
        return {
            'type': 'weather',
            'city': city,
            'original_text': text
        }
    
    # Если нашли город, но нет ключевых слов погоды (типа "в лондоне")
    elif city:
        return {
            'type': 'weather',
            'city': city,
            'original_text': text
        }
    
    # Не нашли город
    return {
        'type': 'unknown',
        'original_text': text
    }


def detect_intent(text):
    """Определяет намерение пользователя"""
    text_lower = text.lower()
    
    # Словарь ключевых слов для разных намерений
    intents = {
        'weather': ['погод', 'температур', 'градус', 'тепл', 'холодн', 'мороз', 
                   'weather', 'temperature', 'forecast'],
        'greeting': ['привет', 'здравствуй', 'добрый', 'hello', 'hi'],
        'farewell': ['пока', 'до свидания', 'прощай', 'bye', 'goodbye'],
        'time': ['время', 'часов', 'time'],
        'help': ['помоги', 'help', 'что умеешь', 'команды'],
    }
    
    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in text_lower:
                return intent
    
    # Если есть город в тексте, возможно это ответ на запрос города
    city = extract_city_from_text(text)
    if city:
        return 'city_provided'
    
    return 'unknown'