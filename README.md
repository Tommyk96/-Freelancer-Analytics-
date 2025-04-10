# Freelancer Income Analytics (FIA)

Аналитический инструмент для обработки доходов фрилансеров с использованием CLI и LLM.

## Описание

Freelancer Income Analytics (FIA) — это Python-приложение, которое позволяет анализировать доходы фрилансеров на основе различных параметров, таких как регион проживания, способ оплаты и уровень опыта. Проект использует pandas для обработки данных, Typer для CLI и LLM для генерации текстовых ответов.

## Возможности

- Анализ распределения доходов по регионам.
- Сравнение доходов по способам оплаты (например, криптовалюта vs другие).
- Подсчёт процента фрилансеров с определёнными характеристиками (например, эксперты с < 100 проектами).
- Поддержка кэширования и логирования.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/<ваш-username>/FreelancerIncomeAnalytics.git
   cd FreelancerIncomeAnalytics
   ```
2. Создайте виртуальное окружение и активируйте его:

   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
3. Установите зависимости:

   pip install -r requirements.txt
4. Настройте **.env** в корне проекта:

   OPENROUTER_API_KEY=your_openrouter_api_key
   API_URL=https://openrouter.ai/api/v1/chat/completions
   DATA_PATH=/path/to/your/freelancer_earnings_bd.csv
5. ## Использование

   Запустите CLI с запросом:


    python3 -m freelancer-analytics.cli.main "Как распределяется доход фрилансеров в зависимости от региона     проживания?" --verbose

    python3 -m freelancer-analytics.cli.main "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?" --verbose

    python3 -m freelancer-analytics.cli.main "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?
" --verbose
