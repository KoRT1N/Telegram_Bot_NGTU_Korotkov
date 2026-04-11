import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class BERTIntentClassifier:
    def __init__(self, model_path="bert_intent_model"):
        print("Загрузка BERT модели...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
        
        self.id2label = self.model.config.id2label
        print(f"   ✅ Модель загружена. Доступно интентов: {len(self.id2label)}")
        print(f"   Интенты: {list(self.id2label.values())}")
    
    def predict_intent(self, text, threshold=0.5):
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=64,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            confidence = torch.max(probabilities).item()
            predicted_class = torch.argmax(logits, dim=1).item()
            intent = self.id2label[predicted_class]
        
        if confidence < threshold:
            return 'unknown', confidence
        
        return intent, confidence

bert_classifier = BERTIntentClassifier()