import pandas as pd
import numpy as np
from typing import Optional
from pathlib import Path
import logging
from config.settings import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    REQUIRED_COLUMNS = ['Earnings_USD', 'Job_Category', 'Payment_Method']
    NUMERIC_COLS = ['Earnings_USD', 'Hourly_Rate', 'Job_Success_Rate']
    CATEGORICAL_COLS = ['Job_Category', 'Payment_Method', 'Platform']
    
    def __init__(self):
        self.df = self._load_and_validate_data()

    def _load_and_validate_data(self) -> pd.DataFrame:
        """Загрузка данных с валидацией"""
        try:
            if not Path(settings.DATA_PATH).exists():
                raise FileNotFoundError(f"Файл данных не найден: {settings.DATA_PATH}")
            
            df = pd.read_csv(settings.DATA_PATH)
            logger.info(f"Данные загружены. Исходный размер: {df.shape}")
            
            # Проверка обязательных колонок
            missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Отсутствуют обязательные колонки: {missing_cols}")
            
            return self._clean_data(df)
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {str(e)}")
            raise

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Комплексная очистка данных"""
        # Удаление дубликатов
        initial_rows = len(df)
        df = df.drop_duplicates().copy()
        logger.info(f"Удалено дубликатов: {initial_rows - len(df)}")
        
        # Обработка числовых колонок
        for col in self.NUMERIC_COLS:
            if col in df.columns:
                # Замена отрицательных значений на NaN
                df[col] = np.where(df[col] < 0, np.nan, df[col])
                # Заполнение медианой
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                logger.info(f"Обработана колонка {col}: заполнено {df[col].isna().sum()} пропусков")
        
        # Обработка категориальных колонок
        for col in self.CATEGORICAL_COLS:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', np.nan)
                df[col] = df[col].fillna('unknown')
                logger.info(f"Уникальных значений в {col}: {df[col].nunique()}")
        
        # Дополнительные проверки
        if 'Earnings_USD' in df.columns:
            df = df[df['Earnings_USD'] <= df['Earnings_USD'].quantile(0.99)]  # Удаление выбросов
            logger.info(f"Оставлено записей после фильтрации выбросов: {len(df)}")
        
        return df

    def get_data(self, filters: Optional[dict] = None) -> pd.DataFrame:
        """
        Возвращает данные с возможностью фильтрации
        
        Параметры:
            filters: словарь с фильтрами {колонка: значение}
        
        Возвращает:
            Отфильтрованный DataFrame
        """
        df = self.df.copy()
        print(f"Столбцы данных: {df.columns.tolist()}")  # Добавлен вывод столбцов
        
        if filters:
            for column, value in filters.items():
                if column in df.columns:
                    if isinstance(value, (list, tuple)):
                        df = df[df[column].isin(value)]
                    else:
                        df = df[df[column] == value]
            logger.info(f"Применены фильтры. Осталось записей: {len(df)}")
        
        return df

    def get_income_stats(self) -> dict:
        """Возвращает базовую статистику по доходам"""
        if 'Earnings_USD' not in self.df.columns:
            raise ValueError("Колонка 'Earnings_USD' отсутствует в данных")
        
        return {
            'mean': float(self.df['Earnings_USD'].mean()),
            'median': float(self.df['Earnings_USD'].median()),
            'min': float(self.df['Earnings_USD'].min()),
            'max': float(self.df['Earnings_USD'].max()),
            'count': int(len(self.df))
        }