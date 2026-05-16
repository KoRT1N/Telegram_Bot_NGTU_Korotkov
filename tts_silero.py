import torch
import io
import re
import os
import hashlib
from pathlib import Path
import logging
import numpy as np
from scipy.io import wavfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SileroTTS:
    def __init__(self, language="ru", speaker="aidar", sample_rate=48000):
        """
        Инициализация Silero TTS
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sample_rate = sample_rate
        self.language = language
        self.speaker = speaker
        
        # Создаем папку для кэша
        self.cache_dir = Path("audio_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Загружаем модель
        logger.info(f"Загрузка Silero TTS модели на {self.device}...")
        
        local_file = 'model.pt'
        
        if not os.path.exists(local_file):
            torch.hub.download_url_to_file(
                'https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                local_file
            )
        
        self.model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        self.model.to(self.device)
        
        # Список доступных голосов
        self.available_speakers = ['aidar', 'baya', 'ksenia', 'xenia', 'eugene', 'random']
        if speaker not in self.available_speakers:
            logger.warning(f"Голос {speaker} не найден. Использую 'aidar'")
            self.speaker = 'aidar'
        
        logger.info(f"✅ Модель загружена. Частота: {self.sample_rate} Гц, Голос: {self.speaker}")
    
    def normalize_text(self, text: str) -> str:
        """Нормализация текста"""
        original = text
        text = text.strip()
        
        # Удаляем эмодзи
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F700-\U0001F77F"
            u"\U0001F780-\U0001F7FF"
            u"\U0001F800-\U0001F8FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U0001FA70-\U0001FAFF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub("", text)
        
        # Обработка температуры
        text = re.sub(r"(\d+)°C", r"\1 градусов Цельсия", text)
        text = re.sub(r"(\d+)°", r"\1 градусов", text)
        text = re.sub(r"(\d+)%", r"\1 процентов", text)
        
        # Математические символы
        text = text.replace("+", " плюс ")
        text = text.replace("-", " минус ")
        text = text.replace("*", " умножить на ")
        text = text.replace("/", " разделить на ")
        text = text.replace("=", " равно ")
        
        # Обрезаем длинные тексты
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        if original != text:
            logger.info(f"Нормализация: '{original[:50]}...' -> '{text[:50]}...'")
        
        return text
    
    def text_to_audio(self, text: str, file_path: str = None) -> bytes:
        """Преобразование текста в аудио (WAV)"""
        normalized_text = self.normalize_text(text)
        
        # Синтез речи
        audio = self.model.apply_tts(
            text=normalized_text,
            speaker=self.speaker,
            sample_rate=self.sample_rate
        )
        
        # Конвертируем в numpy int16 (формат WAV)
        audio_np = (audio.detach().cpu().numpy() * 32767).astype(np.int16)
        
        # Сохраняем через scipy (не требует torchaudio)
        if file_path:
            wavfile.write(file_path, self.sample_rate, audio_np)
            logger.info(f"Аудио сохранено: {file_path}")
            with open(file_path, "rb") as f:
                return f.read()
        
        # Временный файл в памяти
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_np)
        buffer.seek(0)
        return buffer.read()
    
    def get_cached_path(self, text: str) -> str:
        """Путь к кэшированному аудио"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.cache_dir / f"{text_hash}.wav"
    
    def text_to_audio_with_cache(self, text: str) -> bytes:
        """Преобразование с кэшированием"""
        cache_path = self.get_cached_path(text)
        
        if cache_path.exists():
            logger.info(f"Используем кэш: {cache_path}")
            with open(cache_path, "rb") as f:
                return f.read()
        
        audio_bytes = self.text_to_audio(text, str(cache_path))
        return audio_bytes

# Создаем глобальный экземпляр
try:
    tts_engine = SileroTTS()
    TTS_AVAILABLE = True
    logger.info("✅ TTS инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации TTS: {e}")
    TTS_AVAILABLE = False
    tts_engine = None