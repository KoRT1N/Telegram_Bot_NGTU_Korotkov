import spacy
import re
from bert_intent_classifier import bert_classifier

# Загружаем русскую модель spaCy для NER (только для извлечения городов)
try:
    nlp = spacy.load("ru_core_news_md")
    print("✅ spaCy модель (для NER) загружена")
except:
    print("Устанавливаю русскую модель...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_md"])
    nlp = spacy.load("ru_core_news_md")

# База городов с их корнями
CITY_DATABASE = {
    'москв': 'Москва',
    'мск': 'Москва',
    'петербург': 'Санкт-Петербург',
    'питер': 'Санкт-Петербург',
    'ленинград': 'Санкт-Петербург',
    'спб': 'Санкт-Петербург',
    'нижн': 'Нижний Новгород',
    'новгород': 'Нижний Новгород',
    'нн': 'Нижний Новгород',
    'лондон': 'Лондон',
    'париж': 'Париж',
    'берлин': 'Берлин',
    'рим': 'Рим',
    'токио': 'Токио',
    'нью': 'Нью-Йорк',
    'йорк': 'Нью-Йорк',
    'ростов': 'Ростов-на-Дону',
    'казан': 'Казань',
    'екатеринбург': 'Екатеринбург',
    'новосибирск': 'Новосибирск',
}

ENGLISH_CITIES = {
    'london': 'Лондон',
    'moscow': 'Москва',
    'paris': 'Париж',
    'berlin': 'Берлин',
    'rome': 'Рим',
    'tokyo': 'Токио',
    'new york': 'Нью-Йорк',
    'spb': 'Санкт-Петербург',
    'kazan': 'Казань',
}

def extract_city_root(word):
    """Извлекает корень слова"""
    word = word.lower()
    endings = ['а', 'у', 'е', 'и', 'ой', 'ою', 'еи', 'ей', 'ом', 'ем', 'ами', 'ях', 'ах']
    
    for ending in endings:
        if word.endswith(ending) and len(word) > len(ending) + 2:
            root = word[:-len(ending)]
            if root in CITY_DATABASE:
                return root
    return word

def find_city_by_root(word):
    """Ищет город по корню"""
    word = word.lower().strip()
    
    if word in CITY_DATABASE:
        return CITY_DATABASE[word]
    
    root = extract_city_root(word)
    if root in CITY_DATABASE:
        return CITY_DATABASE[root]
    
    for city_root, city_name in CITY_DATABASE.items():
        if city_root in word and len(city_root) > 3:
            return city_name
    
    return None

def extract_city_from_text(text):
    """Извлекает город из текста"""
    text_lower = text.lower()
    
    # Проверяем английские названия
    for eng_name, rus_city in ENGLISH_CITIES.items():
        if eng_name in text_lower:
            return rus_city
    
    # Ищем после предлога "в"
    match = re.search(r'[вво]\s+([а-яА-Яa-zA-Z\-]+(?:[-\s][а-яА-Яa-zA-Z\-]+)?)', text_lower)
    if match:
        potential_city = match.group(1).strip()
        words = re.findall(r'[а-яА-Яa-zA-Z\-]+', potential_city)
        for word in words:
            found = find_city_by_root(word)
            if found:
                return found
    
    # Ищем в тексте
    words = re.findall(r'[а-яА-Яa-zA-Z]{4,}', text_lower)
    for word in words:
        found = find_city_by_root(word)
        if found:
            return found
    
    # Используем spaCy
    doc = nlp(text_lower)
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:
            city = ent.text
            found = find_city_by_root(city)
            if found:
                return found
            return city.capitalize()
    
    return None

def extract_days(text):
    """Извлекает количество дней из текста"""
    text_lower = text.lower()
    
    days_map = {
        'завтра': 1,
        'послезавтра': 2,
        'сегодня': 0,
        'tomorrow': 1,
        'today': 0,
        'через один день': 1,
        'через два дня': 2,
        'через три дня': 3,
        'через четыре дня': 4,
        'через пять дней': 5,
        'через шесть дней': 6,
        'через семь дней': 7,
    }
    
    for phrase, days in days_map.items():
        if phrase in text_lower:
            return days
    
    pattern = r'через\s+(\d+)\s+дня?ей?'
    match = re.search(pattern, text_lower)
    if match:
        days = int(match.group(1))
        return min(days, 7)
    
    return None

def detect_intent_fallback(text):
    """Fallback на правила (когда BERT не уверен)"""
    text_lower = text.lower()
    
    # HELP
    if any(word in text_lower for word in ['умеешь', 'функции', 'команды', 'помоги', 'help', 'можешь', 'расскажи о себе']):
        return 'help'
    
    # HOW_ARE_YOU
    if any(word in text_lower for word in ['настроени', 'дела', 'жизн', 'поживаешь', 'самочувствие']):
        return 'how_are_you'
    
    # WEATHER
    if any(word in text_lower for word in ['погод', 'градус', 'температур', 'дожд', 'снег', 'ветер']):
        return 'weather'
    
    # TIME
    if any(word in text_lower for word in ['время', 'час', 'минут', 'секунд']):
        return 'time'
    
    # GREETING
    if any(word in text_lower for word in ['привет', 'здравствуй', 'добрый', 'здорово']):
        return 'greeting'
    
    # FAREWELL
    if any(word in text_lower for word in ['пока', 'свидания', 'прощай', 'увидимся']):
        return 'farewell'
    
    # SET_NAME
    if any(word in text_lower for word in ['зовут', 'имя', 'называй']):
        return 'set_name'
    
    # MATH
    if '+' in text_lower or 'плюс' in text_lower:
        return 'addition'
    if '-' in text_lower or 'минус' in text_lower:
        return 'subtraction'
    if '*' in text_lower or 'умнож' in text_lower:
        return 'multiplication'
    if '/' in text_lower or 'раздел' in text_lower:
        return 'division'
    
    return 'unknown'

def detect_intent_hybrid(text):
    """Гибридное определение интента: BERT + fallback правила"""
    # Пробуем BERT модель
    intent, confidence = bert_classifier.predict_intent(text, threshold=0.5)
    
    print(f"[BERT] intent: {intent}, уверенность: {confidence:.2%}")
    
    if intent != 'unknown' and confidence >= 0.5:
        return intent
    
    # Если BERT не уверен, используем fallback правила
    fallback_intent = detect_intent_fallback(text)
    print(f"[Fallback] intent: {fallback_intent}")
    
    return fallback_intent