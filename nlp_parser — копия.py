import spacy
import re
from intent_classifier import intent_classifier

# Загружаем русскую модель
try:
    nlp = spacy.load("ru_core_news_sm")
    print("✅ spaCy модель загружена")
except:
    print("Устанавливаю русскую модель...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_sm"])
    nlp = spacy.load("ru_core_news_sm")

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
    """Fallback на правила (старая логика)"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['привет', 'здравствуй', 'добрый']):
        return 'greeting'
    elif any(word in text_lower for word in ['пока', 'до свидания', 'прощай']):
        return 'farewell'
    elif any(word in text_lower for word in ['погод', 'температур', 'градус']):
        return 'weather'
    elif any(word in text_lower for word in ['время', 'часов']):
        return 'time'
    elif any(word in text_lower for word in ['как дела', 'как жизнь']):
        return 'how_are_you'
    elif 'зовут' in text_lower:
        return 'set_name'
    elif '+' in text_lower:
        return 'addition'
    elif '-' in text_lower:
        return 'subtraction'
    elif '*' in text_lower:
        return 'multiplication'
    elif '/' in text_lower:
        return 'division'
    
    return 'unknown'

def detect_intent_hybrid(text):
    """Гибридное определение интента: ML + правила"""
    # Пробуем ML модель
    intent, confidence = intent_classifier.predict_intent(text, threshold=0.5)
    
    print(f"ML предсказание: {intent} (уверенность: {confidence:.2%})")
    
    if intent != 'unknown' and confidence > 0.5:
        return intent
    
    # Если ML не уверен, используем fallback
    fallback_intent = detect_intent_fallback(text)
    print(f"Fallback предсказание: {fallback_intent}")
    
    return fallback_intent

# Загружаем модель с векторами
try:
    nlp = spacy.load("ru_core_news_md")
    print("✅ spaCy модель (с векторами) загружена")
except:
    print("Устанавливаю модель...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_md"])
    nlp = spacy.load("ru_core_news_md")

def detect_intent_hybrid(text):
    """Гибридное определение интента с embeddings"""
    # Пробуем ML с embeddings
    intent, confidence = intent_classifier_embeddings.predict_intent(text, threshold=0.4)
    
    print(f"[Embeddings] intent: {intent}, confidence: {confidence:.2%}")
    
    if intent != 'unknown':
        return intent
    
    # Fallback на правила
    return detect_intent_fallback(text)

def detect_intent_fallback(text):
    """Правила для случаев низкой уверенности"""
    text_lower = text.lower()
    
    if 'настроени' in text_lower:
        return 'how_are_you'
    if 'погод' in text_lower or 'градус' in text_lower:
        return 'weather'
    if 'время' in text_lower or 'час' in text_lower:
        return 'time'
    if 'привет' in text_lower or 'здравствуй' in text_lower:
        return 'greeting'
    if 'пока' in text_lower or 'свидания' in text_lower:
        return 'farewell'
    if 'дела' in text_lower or 'жизн' in text_lower:
        return 'how_are_you'
    if 'зовут' in text_lower or 'имя' in text_lower:
        return 'set_name'
    if 'плюс' in text_lower or '+' in text_lower:
        return 'addition'
    if 'минус' in text_lower or '-' in text_lower:
        return 'subtraction'
    if 'умнож' in text_lower or '*' in text_lower:
        return 'multiplication'
    if 'раздел' in text_lower or '/' in text_lower:
        return 'division'
    if 'помощ' in text_lower or 'умеешь' in text_lower:
        return 'help'
    
    return 'unknown'