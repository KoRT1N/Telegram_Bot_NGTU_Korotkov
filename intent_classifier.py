import spacy
import joblib
import os

class IntentClassifier:
    def __init__(self):
        self.nlp = None
        self.model = None
        self.vectorizer = None
        self.intents = []
        self.load_models()
    
    def load_models(self):
        """Загрузка обученных моделей"""
        print("Загрузка моделей классификации интентов...")
        
        # Загружаем spaCy
        try:
            self.nlp = spacy.load("ru_core_news_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "ru_core_news_sm"])
            self.nlp = spacy.load("ru_core_news_sm")
        
        # Загружаем ML модель
        if os.path.exists('intent_model.pkl') and os.path.exists('vectorizer.pkl'):
            self.model = joblib.load('intent_model.pkl')
            self.vectorizer = joblib.load('vectorizer.pkl')
            self.intents = self.model.classes_
            print(f"   ✅ Модель загружена. Доступно интентов: {len(self.intents)}")
        else:
            print("   ⚠️ Модель не найдена. Сначала запустите train_intent_model.py")
            self.model = None
    
    def preprocess(self, text):
        """Предобработка текста для модели"""
        if not self.nlp:
            return text.lower()
        
        doc = self.nlp(text.lower())
        tokens = []
        
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space:
                # Обрабатываем числа специально
                if token.like_num:
                    tokens.append('число')
                else:
                    tokens.append(token.lemma_)
        
        return " ".join(tokens)
    
    def predict_intent(self, text, threshold=0.5):
        """Предсказание интента с порогом уверенности"""
        
        # Если модель не загружена, возвращаем unknown
        if self.model is None:
            return 'unknown', 0.0
        
        try:
            # Предобработка
            processed = self.preprocess(text)
            
            # Векторизация
            vector = self.vectorizer.transform([processed])
            
            # Предсказание
            probabilities = self.model.predict_proba(vector)
            confidence = max(probabilities[0])
            intent = self.model.predict(vector)[0]
            
            # Если уверенность низкая, возвращаем unknown
            if confidence < threshold:
                return 'unknown', confidence
            
            return intent, confidence
            
        except Exception as e:
            print(f"Ошибка при предсказании: {e}")
            return 'unknown', 0.0
    
    def predict_intent_with_fallback(self, text, fallback_func=None, threshold=0.5):
        """Гибридное предсказание: ML + fallback"""
        intent, confidence = self.predict_intent(text, threshold)
        
        if intent == 'unknown' and fallback_func:
            # Пробуем fallback
            fallback_intent = fallback_func(text)
            if fallback_intent:
                return fallback_intent, confidence
        
        return intent, confidence

# Создаем глобальный экземпляр
intent_classifier = IntentClassifier()