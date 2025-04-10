import os
import requests
import logging
import pandas as pd
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('freelancer_analytics.log')
    ]
)

class Settings:
    def __init__(self):
        load_dotenv()
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.API_URL = os.getenv("API_URL")
        self.DATA_PATH = "/home/fantomas/Documents/archive/freelancer_earnings_bd.csv"
        self.MODEL = "mistralai/mixtral-8x7b-instruct"
        self._validate_settings()
    
    def _validate_settings(self):
        if not self.OPENROUTER_API_KEY:
            raise ValueError("❌ API ключ не найден. Проверьте файл .env")
        if not self.API_URL:
            raise ValueError("❌ API_URL не найден. Проверьте файл .env")
        if not os.path.exists(self.DATA_PATH):
            raise FileNotFoundError(f"❌ Файл данных не найден: {self.DATA_PATH}")

class DataHandler:
    def __init__(self, data_path):
        self.data_path = data_path
        self._df = None
    
    @property
    def df(self):
        if self._df is None:
            self._load_data()
        return self._df
    
    def _load_data(self):
        try:
            logging.info(f"📥 Загрузка данных из файла: {self.data_path}")
            df = pd.read_csv(self.data_path)

            if 'Earnings_USD' not in df.columns:
                raise ValueError("❌ Столбец 'Earnings_USD' не найден в данных")

            df['Earnings_USD'] = pd.to_numeric(df['Earnings_USD'], errors='coerce')
            df = df.dropna(subset=['Earnings_USD'])

            # Удалим выбросы (1-й и 99-й перцентиль)
            q_low, q_high = df['Earnings_USD'].quantile([0.01, 0.99])
            df = df[df['Earnings_USD'].between(q_low, q_high)]

            self._df = df
            logging.info(f"✅ Данные загружены. Размер: {df.shape}")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки данных: {e}")
            raise

class LLMGenerator:
    def __init__(self, settings):
        self.settings = settings
        self.headers = {
            "Authorization": f"Bearer {self.settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, query: str, data_stats: dict) -> str:
        """Анализ данных через LLM API"""
        prompt = self._build_prompt(query, data_stats)

        try:
            response = requests.post(
                self.settings.API_URL,
                headers=self.headers,
                json={
                    "model": self.settings.MODEL,
                    "messages": [
                        {"role": "system", "content": "Ты аналитик данных. Отвечай точно и кратко."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                timeout=15
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"❌ API ошибка: {e}")
            return f"Не удалось получить анализ: {e}"
    
    def _build_prompt(self, query: str, data_stats: dict) -> str:
        stats_str = "\n".join(
            f"- {key.replace('_', ' ').capitalize()}: {value:.2f}{' USD' if 'avg' in key or 'difference' in key else ' %' if 'percentage' in key else ''}"
            for key, value in data_stats.items() if isinstance(value, (int, float))
        )
        instruction = "Ответь на вопрос, используя только эти данные. Для сравнений укажи разницу в доходах в USD, если применимо."
        return f"""
    Вопрос: {query}
    Данные: 
    {stats_str}
    {instruction}
    """.strip()

def main():
    try:
        settings = Settings()
        data_handler = DataHandler(settings.DATA_PATH)
        df = data_handler.df

        stats = {
            'mean': df['Earnings_USD'].mean(),
            'median': df['Earnings_USD'].median(),
            'count': len(df),
            'min': df['Earnings_USD'].min(),
            'max': df['Earnings_USD'].max()
        }

        logging.info(f"📊 Статистика доходов: {stats}")

        analyzer = LLMGenerator(settings)
        query = "Как распределяется доход фрилансеров в зависимости от региона проживания?"
        query = "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?"
        analysis = analyzer.generate_response(query, stats)
        print(f"\n📊 Результаты анализа:\n"
              f"Средний доход: {stats['mean']:.2f} USD\n"
              f"Медианный доход: {stats['median']:.2f} USD\n"
              f"\n🔍 Анализ ИИ:\n{analysis}")

    except Exception as e:
        logging.error(f"❌ Ошибка в работе приложения: {e}")
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()

