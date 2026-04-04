import pandas as pd
import spacy
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

print("="*60)
print("ОБУЧЕНИЕ МОДЕЛИ НА WORD EMBEDDINGS (spaCy)")
print("="*60)

# Загружаем среднюю модель spaCy (с word vectors)
print("\n1. Загрузка spaCy модели ru_core_news_md...")
try:
    nlp = spacy.load("ru_core_news_md")
    print(f"   ✅ Модель загружена. Размерность вектора: {nlp.vocab.vectors_length}")
except:
    print("   Устанавливаю русскую модель...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_md"])
    nlp = spacy.load("ru_core_news_md")

def text_to_vector(text):
    """Преобразует текст в вектор с помощью spaCy"""
    doc = nlp(text.lower())
    # Возвращаем вектор всего документа (среднее арифметическое векторов слов)
    return doc.vector

def preprocess(text):
    """Предобработка для векторизации (очистка)"""
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

# Статистика
print("\n3. Статистика по интентам:")
for intent in df['intent'].unique():
    count = len(df[df['intent'] == intent])
    print(f"   {intent}: {count} примеров")

# Создание векторов
print("\n4. Создание векторных представлений (spaCy embeddings)...")
vectors = []
for i, text in enumerate(df['text']):
    if i % 100 == 0:
        print(f"   Обработано {i}/{len(df)} примеров...")
    vector = text_to_vector(text)
    vectors.append(vector)

X = np.array(vectors)
y = df['intent'].values

print(f"   Размерность X: {X.shape}")

# Разделение на train/test
print("\n5. Разделение на train/test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Обучающая выборка: {X_train.shape[0]} примеров")
print(f"   Тестовая выборка: {X_test.shape[0]} примеров")

# Обучение модели
print("\n6. Обучение модели LogisticRegression...")
model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    C=1.0,
    class_weight='balanced'
)
model.fit(X_train, y_train)

# Оценка модели
print("\n7. Оценка модели...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   Точность на тесте: {accuracy:.2%}")

if X_test.shape[0] > 5:
    print("\n   Детальный отчет:")
    print(classification_report(y_test, y_pred))

# Сохранение модели
print("\n8. Сохранение модели...")
joblib.dump(model, "intent_model_embeddings.pkl")
print("   ✅ Модель сохранена в intent_model_embeddings.pkl")

# Тестирование на примерах
print("\n" + "="*60)
print("ТЕСТИРОВАНИЕ НА ПРИМЕРАХ")
print("="*60)

test_examples = {
    "привет как дела": "how_are_you",
    "какая погода в лондоне": "weather",
    "будет ли дождь завтра": "weather",
    "сколько времени": "time",
    "пока до свидания": "farewell",
    "меня зовут Анна": "set_name",
    "2 плюс 2": "addition",
    "10 минус 5": "subtraction",
    "что ты умеешь": "help",
    "как настроение": "how_are_you",
}

correct = 0
for example, expected in test_examples.items():
    vector = text_to_vector(example).reshape(1, -1)
    intent = model.predict(vector)[0]
    proba = model.predict_proba(vector)
    confidence = max(proba[0])
    
    is_correct = intent == expected
    if is_correct:
        correct += 1
    
    status = "✅" if is_correct else "❌"
    print(f"{status} '{example}'")
    print(f"   Ожидалось: {expected} -> Получено: {intent} (уверенность: {confidence:.2%})")

print(f"\nТочность на тестовых примерах: {correct}/{len(test_examples)} = {correct/len(test_examples):.2%}")

print("\n✅ Обучение на word embeddings завершено!")
