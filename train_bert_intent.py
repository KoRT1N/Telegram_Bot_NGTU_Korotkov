import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

print("="*60)
print("FINE-TUNING BERT ДЛЯ КЛАССИФИКАЦИИ ИНТЕНТОВ")
print("="*60)

# Загрузка датасета
print("\n1. Загрузка датасета...")
df = pd.read_csv('dataset.csv')
print(f"   Загружено {len(df)} примеров")

# Создаем маппинг интентов
unique_intents = df['intent'].unique()
label2id = {label: idx for idx, label in enumerate(unique_intents)}
id2label = {idx: label for label, idx in label2id.items()}
num_labels = len(unique_intents)

print(f"   Интенты ({num_labels}): {list(label2id.keys())}")

# Добавляем числовые метки
df['label'] = df['intent'].map(label2id)

# Разделение на train/val
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['text'].tolist(),
    df['label'].tolist(),
    test_size=0.2,
    random_state=42,
    stratify=df['label']
)

print(f"\n2. Разделение данных:")
print(f"   Обучающая выборка: {len(train_texts)} примеров")
print(f"   Валидационная: {len(val_texts)} примеров")

# Загрузка токенизатора и модели (используем rubert-tiny2)
print("\n3. Загрузка модели rubert-tiny2...")
MODEL_NAME = "cointegrated/rubert-tiny2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True  # Добавляем этот параметр
)

# Токенизация
print("\n4. Токенизация текстов...")

def tokenize_function(texts):
    return tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=64,  # Для tiny можно меньше
        return_tensors="pt"
    )

train_encodings = tokenize_function(train_texts)
val_encodings = tokenize_function(val_texts)

# Создание PyTorch Dataset
class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = IntentDataset(train_encodings, train_labels)
val_dataset = IntentDataset(val_encodings, val_labels)

# Функция для вычисления метрик
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return {'accuracy': accuracy_score(labels, predictions)}

# Настройки обучения
print("\n5. Настройка обучения...")
training_args = TrainingArguments(
    output_dir="./bert_intent_model",
    num_train_epochs=10,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
    learning_rate=2e-4,  # Для tiny можно выше
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    report_to="none"
)

# Создание Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# Обучение
print("\n6. Запуск обучения...")
trainer.train()

# Оценка модели
print("\n7. Оценка модели на валидации...")
eval_results = trainer.evaluate()
print(f"   Точность: {eval_results['eval_accuracy']:.2%}")

# Сохранение модели
print("\n8. Сохранение модели...")
model.save_pretrained("bert_intent_model")
tokenizer.save_pretrained("bert_intent_model")
print("   ✅ Модель сохранена в bert_intent_model/")

print("\n✅ Fine-tuning BERT завершен!")