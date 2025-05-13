from main.scraper import scrape
from main.parser import parse_html, load_parsed_in_db
from datetime import datetime
import logging

def run_pipeline(url_key="kindle"):
    # Запускаем скрапер и получаем суффикс директории
    dir_suffix = scrape(enable_pagination=False, url_key=url_key)
    
    # Разбиваем суффикс директории на составляющие
    parts = dir_suffix.split("_")
    if len(parts) < 2:
        logging.error(f"Некорректный формат суффикса директории: {dir_suffix}")
        return None
        
    time_marker = parts[0]
    name_marker = parts[1] if len(parts) > 1 else ""
    
    # Используем полученные маркеры для парсинга
    parse_html(time_marker=time_marker)
    
    # Загружаем данные в БД с указанием категории
    load_parsed_in_db(time_marker=time_marker, name_marker=name_marker)
    
    # Возвращаем суффикс директории как ключ для словаря результатов
    result = {
        'time_marker': time_marker,
        'name_marker': name_marker,
        'full_key': dir_suffix
    }
    return result

if __name__ == "__main__":
    # Запускаем пайплайн и получаем ключ результата
    result_key = run_pipeline()
    print(f"Пайплайн завершен. Ключ результата: {result_key}")

