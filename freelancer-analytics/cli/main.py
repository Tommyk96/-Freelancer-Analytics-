import typer
import hashlib
import pandas as pd
from typing import Dict, Any
from core.data_processing import DataProcessor
from core.query_analysis import QueryAnalyzer
from core.caching import DataCache
from core.logging import QueryLogger
from core.llm_integration import LLMGenerator
from config.settings import Settings
import os
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()
cache = DataCache()
query_logger = QueryLogger()
settings = Settings()
llm_generator = LLMGenerator(settings)

def _prepare_income_data(df: pd.DataFrame, analyzed_query: dict) -> Dict[str, Any]:
    if 'Earnings_USD' not in df.columns:
        raise ValueError("Столбец 'Earnings_USD' не найден в данных")

    stats = {}
    if analyzed_query['type'] == 'comparison' and 'payment_method' in analyzed_query['params']:
        if 'Payment_Method' not in df.columns:
            stats["error"] = "Данные о способах оплаты отсутствуют"
        else:
            crypto_data = df[df['Payment_Method'] == 'Cryptocurrency']['Earnings_USD']
            other_data = df[df['Payment_Method'] != 'Cryptocurrency']['Earnings_USD']
            crypto_avg = float(crypto_data.mean()) if not crypto_data.empty else 0.0
            other_avg = float(other_data.mean()) if not other_data.empty else 0.0
            stats = {
                "statistics": {
                    "crypto_avg": crypto_avg,
                    "other_avg": other_avg,
                    "difference": crypto_avg - other_avg,
                    "crypto_data_missing": crypto_data.empty
                }
            }

    elif analyzed_query['type'] == 'distribution' and analyzed_query['subtype'] == 'trend_by' and 'region' in analyzed_query['params']:
        if 'Client_Region' not in df.columns:  # Замена 'Region' на 'Client_Region'
            stats["error"] = "Данные о регионах клиентов отсутствуют"
        else:
            region_stats = df.groupby('Client_Region')['Earnings_USD'].agg(['mean', 'count']).to_dict('index')
            stats = {
                "statistics": {f"{region}_avg": stats['mean'] for region, stats in region_stats.items()}
            }

    elif analyzed_query['type'] == 'percentage' and analyzed_query['subtype'] == 'expert_projects':
        if 'Experience_Level' not in df.columns or 'Job_Completed' not in df.columns:  # Замена столбцов
            stats["error"] = "Данные об уровне опыта или количестве выполненных работ отсутствуют"
        else:
            experts = df[df['Experience_Level'] == 'Expert']  # Предполагаем, что 'Expert' — значение для экспертов
            threshold = analyzed_query.get('threshold', 100)
            less_than = experts[experts['Job_Completed'] < threshold]
            stats = {
                "statistics": {
                    "expert_count": int(len(experts)),
                    "less_than_count": int(len(less_than)),
                    "percentage": float(len(less_than) / len(experts) * 100) if len(experts) > 0 else 0.0
                }
            }

    else:
        income_data = df['Earnings_USD']
        stats = {
            "statistics": {
                "average": float(income_data.mean()),
                "median": float(income_data.median()),
                "min": float(income_data.min()),
                "max": float(income_data.max()),
                "count": int(len(income_data))
            }
        }

    return stats

@app.command()
def ask(
    query: str,
    use_cache: bool = typer.Option(True, help="Использовать кэширование"),
    verbose: bool = typer.Option(False, help="Подробный вывод")
):
    cache_key = f"query:{hashlib.md5(query.encode()).hexdigest()}"
    
    if use_cache and (cached_response := cache.get(cache_key)):
        if verbose:
            typer.echo("ℹ️ Используется кэшированный ответ")
        typer.echo(f"\n📤 Ответ: {cached_response}")
        query_logger.log(query, "INFO", "Ответ взят из кэша")
        return

    try:
        processor = DataProcessor()
        df = processor.get_data()
        
        query_analyzer = QueryAnalyzer()
        analyzed_query = query_analyzer.analyze(query)
        print(f"Analyzed query: {analyzed_query}")
        prepared_data = _prepare_income_data(df, analyzed_query)
        
        if verbose:
            typer.echo(f"✅ Загружено {len(df)} записей")
            typer.echo("📊 Статистика:")
            if "error" in prepared_data:
                typer.echo(f"• Ошибка: {prepared_data['error']}")
            else:
                stats = prepared_data["statistics"]
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        unit = " USD" if "avg" in key or "difference" in key else " %" if "percentage" in key else ""
                        typer.echo(f"• {key.replace('_', ' ').capitalize()}: {value:.2f}{unit}")
                    else:
                        typer.echo(f"• {key.replace('_', ' ').capitalize()}: {value}")

        if "error" in prepared_data:
            response = f"Невозможно ответить на запрос: {prepared_data['error']}."
        else:
            response = llm_generator.generate_response(query, prepared_data['statistics'])
        
        if use_cache:
            cache.set(cache_key, response)
        
        query_logger.log(query, "INFO", "Запрос успешно обработан")
        typer.echo(f"\n📤 Ответ:\n{response}")
        
    except ValueError as e:
        error_msg = f"Ошибка данных: {str(e)}"
        typer.echo(f"❌ {error_msg}")
        query_logger.log(query, "ERROR", error_msg)
    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"
        typer.echo(f"⚠️ {error_msg}")
        query_logger.log(query, "ERROR", error_msg)

if __name__ == "__main__":
    app()