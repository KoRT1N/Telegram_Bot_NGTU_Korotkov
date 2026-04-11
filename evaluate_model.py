import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import numpy as np

print("="*60)
print("ОЦЕНКА ТОЧНОСТИ BERT МОДЕЛИ")
print("="*60)

# Загрузка модели
print("\n1. Загрузка модели...")
model_path = "bert_intent_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()

# Загрузка датасета
print("\n2. Загрузка датасета...")
df = pd.read_csv('dataset.csv')
print(f"   Всего примеров: {len(df)}")

# Создаем маппинг
unique_intents = df['intent'].unique()
label2id = {label: idx for idx, label in enumerate(unique_intents)}
id2label = {idx: label for label, idx in label2id.items()}

# Добавляем метки
df['label'] = df['intent'].map(label2id)

# Предсказания
print("\n3. Предсказания на всех примерах...")
predictions = []
true_labels = []

for idx, row in df.iterrows():
    text = row['text']
    true_label = row['label']
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=64, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted = torch.argmax(logits, dim=1).item()
    
    predictions.append(predicted)
    true_labels.append(true_label)
    
    if (idx + 1) % 100 == 0:
        print(f"   Обработано {idx + 1}/{len(df)} примеров")

# Общая точность
accuracy = accuracy_score(true_labels, predictions)
print(f"\n📊 ОБЩАЯ ТОЧНОСТЬ: {accuracy:.2%}")

# Детальный отчет по каждому интенту
print("\n📋 ДЕТАЛЬНЫЙ ОТЧЕТ ПО КАЖДОМУ ИНТЕНТУ:")
print("="*60)
print(classification_report(true_labels, predictions, target_names=unique_intents))

# Матрица ошибок
print("\n📊 МАТРИЦА ОШИБОК (где модель путается):")
print("="*60)

from collections import defaultdict
confusion = defaultdict(lambda: defaultdict(int))

for true, pred in zip(true_labels, predictions):
    true_intent = id2label[true]
    pred_intent = id2label[pred]
    if true_intent != pred_intent:
        confusion[true_intent][pred_intent] += 1

for true_intent, errors in confusion.items():
    if errors:
        print(f"\n{true_intent} часто путается с:")
        for pred_intent, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"   → {pred_intent}: {count} раз")

# Оценка на тестовых фразах
print("\n" + "="*60)
print("ТЕСТ НА РАЗНЫХ ФОРМУЛИРОВКАХ")
print("="*60)

test_phrases = [
    ("привет", "greeting"),
    ("здравствуйте", "greeting"),
    ("пока", "farewell"),
    ("до свидания", "farewell"),
    ("какая погода", "weather"),
    ("сколько градусов в лондоне", "weather"),
    ("сколько времени", "time"),
    ("который час", "time"),
    ("как дела", "how_are_you"),
    ("как настроение", "how_are_you"),
    ("меня зовут анна", "set_name"),
    ("мое имя дмитрий", "set_name"),
    ("2 плюс 3", "addition"),
    ("5 + 2", "addition"),
    ("10 минус 5", "subtraction"),
    ("4 умножить на 3", "multiplication"),
    ("10 разделить на 2", "division"),
    ("что ты умеешь", "help"),
    ("помоги", "help"),
]

correct = 0
for text, expected in test_phrases:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=64, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted = torch.argmax(logits, dim=1).item()
        probs = torch.softmax(logits, dim=1)
        confidence = probs[0][predicted].item()
    
    predicted_intent = id2label[predicted]
    is_correct = predicted_intent == expected
    correct += is_correct
    
    status = "✅" if is_correct else "❌"
    print(f"{status} '{text}'")
    print(f"   Ожидалось: {expected} → Получено: {predicted_intent} (уверенность: {confidence:.2%})")

print(f"\n🎯 Точность на тестовых фразах: {correct}/{len(test_phrases)} = {correct/len(test_phrases):.2%}")