import re
from typing import Dict, Any, List, Tuple
import logging


class QueryLogger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(), logging.FileHandler('query_logs.log')]
        )

    def log(self, query: str, level: str, message: str):
        log_message = f"{level.upper()}: {message} - {query}"
        logging.log(getattr(logging, level.upper(), logging.INFO), log_message)
        print(log_message)


class QueryAnalyzer:
    QUERY_PATTERNS: Dict[str, List[Tuple[str, str]]] = {
        'comparison': [
            (r"(насколько|во сколько раз) (выше|ниже|больше|меньше)", "magnitude_comparison"),
            (r"(сравни|разница между) (.+?) и (.+)", "direct_comparison"),
            (r"кто (зарабатывает|получает) (больше|меньше): (.+?) или (.+)", "group_comparison")
        ],
        'distribution': [
            (r"распределение (доход[а-я]*|зарплат[а-я]*) по (.+)", "distribution_by"),
            (r"как (распределяется|изменяются|варьируются) (доход[а-я]*|зарплат[а-я]*) .*в зависимости от (.+)", "trend_by"),  # С .* для гибкости
            (r"процент фрилансеров с (.+)", "percentage_with")
        ],
        'percentage': [
            (r"какой процент фрилансеров.*(эксперт[а-я]*).*менее (\d+)", "expert_projects"),
            (r"сколько процентов.*выполнил[ио] менее (\d+)", "projects_threshold")
        ],
        'correlation': [
            (r"как (.+) влияет на доход", "influence"),
            (r"связь между (.+) и доходом", "relationship"),
            (r"зависит ли доход от (.+)", "dependency")
        ],
        'extreme': [
            (r"(максимальн|минимальн)(ый|ая) (зарплата|доход)", "extreme_values"),
            (r"топ-\d+ (по зарплате|по доходам)", "top_values")
        ],
        'average': [
            (r"(средн|осреднен)(ый|ая) (зарплата|доход)", "average_value"),
            (r"какой средний доход", "simple_average")
        ]
    }

    PARAM_EXTRACTORS: Dict[str, List[Tuple[str, str]]] = {
        'payment_method': [
            (r"(криптовалют[а-я]*)", "crypto"),
            (r"(банковск[а-я]* перевод[а-я]*)", "bank_transfer"),
            (r"(paypal|пайпал)", "paypal")
        ],
        'experience': [
            (r"(опыт[а-я]*|стаж[а-я]*) (\d+ [летгода]+)", "experience_years"),
            (r"(эксперт[а-я]*|профессионал[а-я]*)", "expert"),
            (r"(новичок[а-я]*|начинающ[а-я]*)", "beginner")
        ],
        'region': [
            (r"(регион[а-я]*|област[а-я]*)", "region"),
            (r"(страна[а-я]*)", "country"),
            (r"(город[а-я]*)", "city")
        ],
        'job_category': [
            (r"(веб-?разработк[а-я]*|web-?development)", "web_development"),
            (r"(мобильн[а-я]* разработк[а-я]*)", "mobile_development"),
            (r"(дизайн[а-я]*)", "design")
        ]
    }

    def analyze(self, query: str) -> Dict[str, Any]:
        query = query.lower().strip()
        analysis = {
            "type": "unknown",
            "subtype": None,
            "params": {},
            "groups": [],
            "original_query": query
        }

        # Отладка: проверяем совпадения шаблонов
        print(f"Analyzing query: {query}")
        for query_type, patterns in self.QUERY_PATTERNS.items():
            for pattern, subtype in patterns:
                match = re.search(pattern, query)
                if match:
                    print(f"Matched pattern: {pattern}, type: {query_type}, subtype: {subtype}")
                    analysis["type"] = query_type
                    analysis["subtype"] = subtype
                    if match.groups():
                        analysis["groups"].extend([g for g in match.groups() if g is not None])
                    break
            if analysis["type"] != "unknown":
                break
        if analysis["type"] == "unknown":
            print("No pattern matched!")

        # Извлечение параметров
        for param_type, extractors in self.PARAM_EXTRACTORS.items():
            for pattern, param_value in extractors:
                matches = re.findall(pattern, query)
                if matches:
                    analysis["params"][param_type] = True
                    for match in matches:
                        analysis["groups"].extend([g for g in match if g is not None])
                    break

        # Дополнительная обработка для числовых параметров
        if 'experience_years' in analysis["params"]:
            self._extract_experience_years(analysis)

        return analysis

    def _extract_experience_years(self, analysis: Dict[str, Any]) -> None:
        for group in analysis["groups"]:
            if group and re.search(r"\d+ [летгода]+", group):
                years = re.search(r"(\d+)", group)
                if years:
                    analysis["params"]["experience_years"] = int(years.group(1))
                break





