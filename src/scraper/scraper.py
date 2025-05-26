from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from client.selenium.selenium import SeleniumParser

from src.scraper.config import *
from src.scraper.utils import generate_data_directory, create_data_directory, check_and_cleanup_directory
from src.scraper.saver import save_items_html


def _initialize_scraping_session(url_key):
    """
    Инициализирует сессию скрейпинга: создает директории и возвращает настройки
    """
    if url_key not in SCRAPING_URLS:
        raise ValueError(f"Неизвестный url_key: {url_key}. Доступные: {list(SCRAPING_URLS.keys())}")
    
    data_dir, dir_suffix = generate_data_directory(DEFAULT_DATA_DIR, url_key)
    create_data_directory(data_dir)
    working_url = SCRAPING_URLS[url_key]
    
    return data_dir, dir_suffix, working_url


def _load_initial_page(parser, working_url, data_dir):
    """
    Загружает первую страницу и сохраняет данные
    """
    parser.go_to_page(working_url)
    parser.refresh_page()
    parser.wait_for_element(By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR, timeout=WAIT_TIME)
    print("Контейнер с объявлениями загружен")
    
    return save_items_html(parser.driver, 1, save_full_page=SAVE_FULL_PAGE, data_dir=data_dir)


def _process_pagination(parser: SeleniumParser, data_dir: str) -> tuple[int, int]:
    """
    Обрабатывает пагинацию и сохраняет данные со всех страниц
    """
    page_num = 2
    total_items = 0
    
    for driver_instance in parser.handle_pagination(
        NEXT_BUTTON_LOCATOR[0],
        NEXT_BUTTON_LOCATOR[1],
        max_pages=MAX_PAGES
    ):
        items_count = save_items_html(
            driver_instance,
            page_num,
            save_full_page=SAVE_FULL_PAGE,
            data_dir=data_dir,
        )
        total_items += items_count
        page_num += 1
        print("-" * 30)
    
    return total_items, page_num - 1


def _finalize_scraping(data_dir, success, total_items, dir_suffix):
    """
    Завершает процесс скрейпинга: проверяет результаты и очищает директории
    """
    if not check_and_cleanup_directory(data_dir):
        print("Директория была удалена из-за недостатка данных")
        return None
    
    print(f"Сохранено {total_items} объявлений")
    return dir_suffix


def scrape(enable_pagination=True, url_key=None):
    """
    Основная функция скрейпинга объявлений с Avito
    """
    if url_key is None:
        raise ValueError("url_key не может быть None")
    
    # Инициализация
    data_dir, dir_suffix, working_url = _initialize_scraping_session(url_key)
    success = False
    total_items = 0
    
    try:
        with SeleniumParser(headless=True) as parser:
            total_items = _load_initial_page(parser, working_url, data_dir)
            
            if enable_pagination:
                pagination_items, pages_processed = _process_pagination(parser, data_dir)
                total_items += pagination_items
                print(f"\nВсего сохранено {total_items} объявлений на {pages_processed} страницах")
            else:
                print("Пагинация отключена. Обработка только первой страницы.")
            
            success = True
            
    except TimeoutException:
        print("Не удалось загрузить страницу или найти контейнер с объявлениями.")
        raise
    except Exception as e:
        print(f"Ошибка при выполнении скрейпинга: {e}")
        raise
    finally:
        result = _finalize_scraping(data_dir, success, total_items, dir_suffix)
        print("\nРабота парсера завершена.")
        return result


def main():
    """Точка входа для запуска скрейпера"""
    scrape(url_key="north_face_jackets")


if __name__ == "__main__":
    main()
