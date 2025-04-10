import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
import os

CACHE_DIR = Path("cache")
CACHE_EXPIRY_DAYS = 7

class DataCache:
    def __init__(self):
        CACHE_DIR.mkdir(exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Генерирует путь к файлу кэша на основе ключа"""
        return CACHE_DIR / f"{hashlib.md5(key.encode()).hexdigest()}.json"
    
    def get(self, key: str) -> Any:
        """Получает данные из кэша"""
        cache_file = self._get_cache_path(key)
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                
            # Проверка срока годности
            cache_time = datetime.fromisoformat(data["timestamp"])
            if datetime.now() - cache_time > timedelta(days=CACHE_EXPIRY_DAYS):
                cache_file.unlink()
                return None
                
            return data["data"]
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink()
            return None
    
    def set(self, key: str, data: Any) -> None:
        """Сохраняет данные в кэш"""
        cache_file = self._get_cache_path(key)
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)