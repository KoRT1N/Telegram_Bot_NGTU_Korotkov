import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

print("="*50)
print("ОБУЧЕНИЕ МОДЕЛИ КЛАССИФИКАЦИИ ИНТЕНТОВ")
print("="*50)

# Загружаем русскую модель spaCy
print("\n1. Загрузка spaCy модели...")
try:
    nlp = spacy.load("ru_core_news_sm")
    print("   ✅ spaCy модель загружена")
except:
    print("   Устанавливаю русскую модель...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_sm"])
    nlp = spacy.load("ru_core_news_sm")

def preprocess(text):
    """Предобработка текста: лемматизация, удаление стоп-слов и пунктуации"""
    doc = nlp(text.lower())
    tokens = []
    
    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:
            tokens.append(token.lemma_)
    
    return " ".join(tokens)

# Загрузка датасета
print("\n2. Загрузка датасета...")
df = pd.read_csv('dataset.csv')
print(f"   Загружено {len(df)} примеров")
print(f"   Интенты: {df['intent'].unique().tolist()}")

# Предобработка текстов
print("\n3. Предобработка текстов...")
processed_texts = [preprocess(text) for text in df['text']]
print(f"   Пример предобработки:")
print(f"   'какая погода в москве' -> '{preprocess('какая погода в москве')}'")

# Создание TF-IDF векторов
print("\n4. Создание TF-IDF векторов...")
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X = vectorizer.fit_transform(processed_texts)
y = df['intent'].values
print(f"   Размерность признаков: {X.shape}")

# Разделение на train/test
print("\n5. Разделение на train/test...")
if len(df) < 50 or len(df['intent'].unique()) > len(df) * 0.2:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print("   Используем обычное разделение (без стратификации)")
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("   Используем стратифицированное разделение")

# Исправлено: используем .shape[0] вместо len()
print(f"   Обучающая выборка: {X_train.shape[0]} примеров")
print(f"   Тестовая выборка: {X_test.shape[0]} примеров")

# Проверка на наличие данных в тестовой выборке
if X_test.shape[0] == 0:
    print("\n⚠️ ВНИМАНИЕ: Тестовая выборка пуста!")
    print("   Использую все данные для обучения...")
    X_train, y_train = X, y
    X_test, y_test = X[:1], y[:1]  # берем хотя бы один пример для теста

# Обучение модели
print("\n6. Обучение модели LogisticRegression...")
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# Оценка модели
print("\n7. Оценка модели...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   Точность на тесте: {accuracy:.2%}")

if X_test.shape[0] > 1 and len(set(y_test)) > 1:
    print("\n   Детальный отчет:")
    print(classification_report(y_test, y_pred))

# Сохранение модели
print("\n8. Сохранение модели...")
joblib.dump(model, "intent_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
print("   ✅ Модель сохранена в intent_model.pkl")
print("   ✅ Векторизатор сохранен в vectorizer.pkl")

# Тестирование на примерах
print("\n" + "="*50)
print("ТЕСТИРОВАНИЕ НА ПРИМЕРАХ")
print("="*50)

test_examples = [
    "привет как дела",
    "какая погода в лондоне",
    "будет ли дождь завтра",
    "сколько времени",
    "пока до свидания",
    "меня зовут Анна",
    "2 плюс 2",
    "10 минус 5",
    "что ты умеешь"
]

for example in test_examples:
    processed = preprocess(example)
    vector = vectorizer.transform([processed])
    intent = model.predict(vector)[0]
    proba = model.predict_proba(vector)
    confidence = max(proba[0])
    print(f"'{example}'")
    print(f"  -> {intent} (уверенность: {confidence:.2%})")

print("\n✅ Обучение завершено!")