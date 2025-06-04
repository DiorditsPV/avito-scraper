from avito_subscriber.client.selenium.selenium import SeleniumParser
from avito_subscriber.scraper.config import *
from avito_subscriber.scraper.utils import generate_data_directory, create_data_directory, check_and_cleanup_directory
from avito_subscriber.scraper.saver import save_items_html
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import datetime


class AvitoScraper:
    """
    Класс для скрейпинга объявлений с Avito
    """
    
    def __init__(self, url_key: str, url: str, data_dir: str = DEFAULT_DATA_DIR, headless: bool = True, external_selenium_url: str = None, max_pages: int = MAX_PAGES):
        """
        Инициализация скрейпера
        """
        self.url_key = url_key # category name
        self.headless = headless
        self.external_selenium_url = external_selenium_url
        self.data_dir = data_dir
        self.dir_suffix = None # timestamp + category name
        self.working_url = url
        self.total_items = 0
        self.success = False
        self.max_pages = max_pages
        self.screenshots_dir = "/opt/airflow/screenshots"
    
    def _initialize_session(self):
        """
        Инициализирует сессию скрейпинга: создает директории и настройки
        """
        self.parsing_dir, self.dir_suffix = generate_data_directory(self.data_dir, self.url_key)
        create_data_directory(self.parsing_dir)
        
        # Создаем директорию для скриншотов
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        print(f"Инициализация скрейпинга для категории: {self.url_key}")
        print(f"Рабочая директория: {self.parsing_dir}")
    
    def _save_debug_screenshot(self, parser: SeleniumParser, error_context: str):
        """
        Создает скриншот страницы для диагностики
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_{self.url_key}_{error_context}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            parser.driver.save_screenshot(filepath)
            print(f"Скриншот сохранен для диагностики: {filepath}")
        except Exception as e:
            print(f"Ошибка создания скриншота: {e}")
    
    def _process_all_pages(self, parser: SeleniumParser) -> tuple[int, int]:
        """
        Обрабатывает все страницы: первую и последующие через пагинацию
        """
        print("Загрузка и обработка всех страниц...")
        
        # Загружаем первую страницу
        parser.go_to_page(self.working_url)
        parser.refresh_page()
        
        try:
            parser.wait_for_element(By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR, timeout=WAIT_TIME)
        except TimeoutException as e:
            print(f"Таймаут при ожидании контейнера объявлений на первой странице")
            self._save_debug_screenshot(parser, "timeout_first_page")
            raise
        
        total_items = save_items_html(parser.driver, 1, data_dir=self.parsing_dir)
        print(f"Страница 1: найдено {total_items} объявлений")
        
        # Проверяем есть ли возможность пагинации
        pages_processed = 1
        page_num = 2
        
        # Обрабатываем остальные страницы через пагинацию
        for driver_instance in parser.handle_pagination(
            NEXT_BUTTON_LOCATOR[0],
            NEXT_BUTTON_LOCATOR[1],
            max_pages=self.max_pages
        ):
            items_count = save_items_html(
                driver_instance,
                page_num,
                data_dir=self.parsing_dir,
            )
            total_items += items_count
            print(f"Страница {page_num}: {items_count} объявлений")
            page_num += 1
            pages_processed += 1
            print("-" * 30)
        
        print(f"--- Пагинация завершена: обработано {pages_processed} страниц ---")
        
        return total_items, pages_processed
    
    def _finalize_scraping(self):
        """
        Завершает процесс скрейпинга: проверяет результаты и очищает директории
        """
        print(f"\n=== Финализация скрейпинга ===")
        print(f"Успешность: {self.success}")
        print(f"Всего объявлений: {self.total_items}")
        
        if not check_and_cleanup_directory(self.parsing_dir):
            print("Директория была удалена из-за недостатка данных")
            return None
        
        print(f"Скрейпинг завершен успешно. Сохранено {self.total_items} объявлений")
        return self.dir_suffix
    
    def run(self) -> str:
        """
        Запускает процесс скрейпинга
        """
        try:
            self._initialize_session()
            
            with SeleniumParser(headless=self.headless, remote_selenium_url=self.external_selenium_url) as parser:
                self.total_items, pages_processed = self._process_all_pages(parser)
                print(f"\nИтого: {self.total_items} объявлений на {pages_processed} страницах")
                
                self.success = True
                
        except TimeoutException as e:
            print(f"Таймаут: Не удалось загрузить страницу или найти контейнер с объявлениями")
            raise
        except Exception as e:
            print(f"Критическая ошибка при выполнении скрейпинга: {e}")
            raise
        finally:
            # Финализация и очистка
            result = self._finalize_scraping()
            print("\nРабота скрейпера завершена.")
            return result
    
    def get_stats(self) -> dict:
        """
        Возвращает статистику скрейпинга
        """
        return {
            'url_key': self.url_key,
            'total_items': self.total_items,
            'success': self.success,
            'data_dir': self.parsing_dir,
            'dir_suffix': self.dir_suffix,
            'max_pages': self.max_pages
        }


def scrape():
    url = "https://www.avito.ru/moskva_i_mo/noutbuki/apple-ASgBAgICAUSo5A302WY?cd=1&f=ASgBAQICAUSo5A302WYBQJ7kDcTWzK0QpprGEJjNrRCOza0QkqPEEbKjxBGc2O8R1NjvEbDY7xHCmZYVqOOXFbyxnhU&q=macbook+pro&user=1"
    scraper = AvitoScraper(
        "macbook_pro", 
        url, 
        "data/raw",
        max_pages=10
    )
    result = scraper.run()
    
    # Вывод статистики
    stats = scraper.get_stats()
    print(f"\nСтатистика: {stats}")
    
    return result


if __name__ == "__main__":
    scrape()
   