# intent_classifier_embeddings.py
import spacy
import numpy as np
import joblib
import os

class IntentClassifierEmbeddings:
    def __init__(self):
        self.nlp = None
        self.model = None
        self.load_models()
    
    def load_models(self):
        """Загрузка spaCy модели и классификатора"""
        print("Загрузка spaCy модели ru_core_news_md...")
        try:
            self.nlp = spacy.load("ru_core_news_md")
            print(f"   ✅ Модель загружена. Размерность: {self.nlp.vocab.vectors_length}")
        except:
            print("   Устанавливаю модель...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_md"])
            self.nlp = spacy.load("ru_core_news_md")
        
        if os.path.exists('intent_model_embeddings.pkl'):
            self.model = joblib.load('intent_model_embeddings.pkl')
            print(f"   ✅ Классификатор загружен. Доступно интентов: {len(self.model.classes_)}")
        else:
            print("   ⚠️ Модель не найдена. Запустите train_intent_model_embeddings.py")
            self.model = None
    
    def text_to_vector(self, text):
        """Преобразование текста в вектор"""
        doc = self.nlp(text.lower())
        return doc.vector
    
    def predict_intent(self, text, threshold=0.4):
        """Предсказание интента с порогом уверенности"""
        if self.model is None:
            return 'unknown', 0.0
        
        try:
            vector = self.text_to_vector(text).reshape(1, -1)
            probabilities = self.model.predict_proba(vector)
            confidence = max(probabilities[0])
            intent = self.model.predict(vector)[0]
            
            if confidence < threshold:
                return 'unknown', confidence
            
            return intent, confidence
            
        except Exception as e:
            print(f"Ошибка при предсказании: {e}")
            return 'unknown', 0.0

# Создаем глобальный экземпляр
intent_classifier_embeddings = IntentClassifierEmbeddings()