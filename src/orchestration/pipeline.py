from src.scraper.scraper import scrape
from src.parser.parser import parse_html, load_parsed_in_db
from src.notifier.notifier import TelegramNotifier

def run_pipeline(url_key="kindle"):
    """
    Основная функция оркестрации процессов:
    1. Скрейпинг данных
    2. Парсинг HTML
    3. Сохранение данных
    4. Отправка уведомлений (по необходимости)
    """
    # Здесь будет логика работы пайплайна
    return url_key 