from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from client.selenium.selenium import SeleniumParser

from src.scraper.config import *
from src.scraper.utils import generate_data_directory, create_data_directory, check_and_cleanup_directory
from src.scraper.saver import save_items_html


class AvitoScraper:
    """
    Класс для скрейпинга объявлений с Avito
    """
    
    def __init__(self, url_key: str, url: str, data_dir: str = DEFAULT_DATA_DIR, enable_pagination: bool = True, headless: bool = True, max_pages: int = MAX_PAGES):
        """
        Инициализация скрейпера
        """
        self.url_key = url_key # category name
        self.enable_pagination = enable_pagination
        self.headless = headless
        
        # Состояние скрейпинга
        self.data_dir = data_dir
        self.dir_suffix = None # timestamp + category name
        self.working_url = url
        self.total_items = 0
        self.success = False
        self.max_pages = max_pages
    
    def _initialize_session(self):
        """
        Инициализирует сессию скрейпинга: создает директории и настройки
        """
        self.parsing_dir, self.dir_suffix = generate_data_directory(self.data_dir, self.url_key)
        create_data_directory(self.parsing_dir)
        
        print(f"Инициализация скрейпинга для категории: {self.url_key}")
        print(f"Рабочая директория: {self.parsing_dir}")
    
    def _load_initial_page(self, parser: SeleniumParser) -> int:
        """
        Загружает первую страницу и сохраняет данные
        """
        print("Загрузка первой страницы...")
        parser.go_to_page(self.working_url)
        parser.refresh_page()
        parser.wait_for_element(By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR, timeout=WAIT_TIME)
        print("Контейнер с объявлениями загружен")
        
        items_count = save_items_html(
            parser.driver, 
            1, 
            data_dir=self.parsing_dir
        )
        
        print(f"Первая страница: найдено {items_count} объявлений")
        return items_count
    
    def _process_pagination(self, parser: SeleniumParser) -> tuple[int, int]:
        """
        Обрабатывает пагинацию и сохраняет данные со всех страниц
        """
        print("\n--- Начало пагинации ---")
        page_num = 2
        total_pagination_items = 0
        
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
            total_pagination_items += items_count
            print(f"Страница {page_num}: {items_count} объявлений")
            page_num += 1
            print("-" * 30)
        
        pages_processed = page_num - 1
        print(f"--- Пагинация завершена: обработано {pages_processed} страниц ---")
        
        return total_pagination_items, pages_processed
    
    def _finalize_scraping(self):
        """
        Завершает процесс скрейпинга: проверяет результаты и очищает директории
        """
        print(f"\n=== Финализация скрейпинга ===")
        print(f"Успешность: {self.success}")
        print(f"Всего объявлений: {self.total_items}")
        
        if not check_and_cleanup_directory(self.data_dir):
            print("Директория была удалена из-за недостатка данных")
            return None
        
        print(f"Скрейпинг завершен успешно. Сохранено {self.total_items} объявлений")
        return self.dir_suffix
    
    def run(self) -> str:
        """
        Запускает процесс скрейпинга
        """
        try:
            # Инициализация
            self._initialize_session()
            
            with SeleniumParser(headless=self.headless) as parser:
                self.total_items = self._load_initial_page(parser)
                
                # Обработка пагинации
                if self.enable_pagination:
                    pagination_items, pages_processed = self._process_pagination(parser)
                    self.total_items += pagination_items
                    print(f"\nИтого: {self.total_items} объявлений на {pages_processed} страницах")
                else:
                    print("Пагинация отключена. Обработана только первая страница.")
                
                # Отмечаем успешное выполнение
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
            'data_dir': self.data_dir,
            'dir_suffix': self.dir_suffix,
            'pagination_enabled': self.enable_pagination
        }


def scrape(enable_pagination=True, url_key=None, headless=True):
    """
    Функция-обертка для обратной совместимости
    """
    if url_key is None:
        raise ValueError("url_key не может быть None")
    
    scraper = AvitoScraper(url_key, enable_pagination, headless)
    return scraper.run()


def main():
    """Точка входа для запуска скрейпера"""
    url = "https://www.avito.ru/moskva_i_mo/noutbuki/apple-ASgBAgICAUSo5A302WY?cd=1&f=ASgBAQICAUSo5A302WYBQJ7kDcTWzK0QpprGEJjNrRCOza0QkqPEEbKjxBGc2O8R1NjvEbDY7xHCmZYVqOOXFbyxnhU&q=macbook+pro&user=1"
    scraper = AvitoScraper(
        "macbook_pro", 
        url, 
        "data/raw",
        max_pages=10,
        enable_pagination=True)
    result = scraper.run()
    
    # Вывод статистики
    stats = scraper.get_stats()
    print(f"\nСтатистика: {stats}")
    
    return result


if __name__ == "__main__":
    main()
