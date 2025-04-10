import os
import logging
import pandas as pd
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class Settings:
    def __init__(self):
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.API_URL = os.getenv("API_URL")
        self.DATA_PATH = "/home/fantomas/Documents/archive/freelancer_earnings_bd.csv"
        self.MODEL = "mistralai/mixtral-8x7b-instruct"  # Добавляем MODEL

        if not self.OPENROUTER_API_KEY:
            raise ValueError("API ключ не найден. Убедитесь, что в файле .env есть OPENROUTER_API_KEY.")
        if not self.API_URL:
            raise ValueError("API_URL не найден. Убедитесь, что в файле .env указан API_URL.")
        if not os.path.exists(self.DATA_PATH):
            logging.error(f"Файл данных не найден: {self.DATA_PATH}")
            raise FileNotFoundError(f"Файл данных не найден: {self.DATA_PATH}")

settings = Settings()

def fetch_data_from_file():
    logging.info(f"Загрузка данных из файла: {settings.DATA_PATH}")
    try:
        df = pd.read_csv(settings.DATA_PATH)
        logging.info(f"Данные успешно загружены. Всего строк: {len(df)}.")
        return df
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
        return None

if __name__ == "__main__":
    # Получаем данные
    data = fetch_data_from_file()

    # Проверка полученных данных
    if data is not None:
        print("Полученные данные:")
        print(data.head())
    else:
        print("Не удалось загрузить данные.")






