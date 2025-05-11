import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

class SeleniumParser:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            # options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--log-level=3')

        try:
            service = ChromeService(executable_path=ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("WebDriver успешно инициализирован.")
        except Exception as e:
            print(f"Ошибка инициализации WebDriver: {e}")
            raise

    def go_to_page(self, url: str):
        try:
            print(f"Переход на страницу: {url}")
            self.driver.get(url)
        except Exception as e:
            print(f"Ошибка при переходе на URL {url}: {e}")
    
    def refresh_page(self):
        try:
            self.driver.refresh()
        except Exception as e:
            print(f"Ошибка при обновлении страницы: {e}")

    def save_html(self, filepath: str):
        try:
            html_content = self.driver.page_source
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML страницы сохранен в файл: {filepath}")
        except Exception as e:
            print(f"Ошибка при сохранении HTML в файл {filepath}: {e}")

    def wait_for_element(self, locator_type: By, locator_value: str, timeout: int = 10):
        print(f"Ожидание элемента: ({locator_type}, {locator_value}) таймаут {timeout} сек.")
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((locator_type, locator_value)))
            print("Элемент найден.")
            return element
        except TimeoutException:
            print(f"Элемент ({locator_type}, {locator_value}) не найден за {timeout} секунд.")
            raise

    def handle_pagination(self, next_button_locator_type: By, next_button_locator_value: str, max_pages: int = None, delay_between_pages: float = random.uniform(1.0, 3.0)):
        page_count = 0
        while True:
            if max_pages is not None and page_count >= max_pages:
                print(f"Достигнуто максимальное количество страниц ({max_pages}). Завершение пагинации.")
                break

            print(f"Обработка страницы {page_count + 1}...")
            yield self.driver

            page_count += 1

            try:
                print(f"Поиск кнопки 'Далее' ({next_button_locator_type}, {next_button_locator_value})...")
                wait = WebDriverWait(self.driver, 2)
                next_button = wait.until(
                    EC.element_to_be_clickable((next_button_locator_type, next_button_locator_value))
                )

                print("Кнопка 'Далее' найдена и кликабельна. Клик...")
                old_html_element = self.driver.find_element(By.TAG_NAME, "html")

                next_button.click()

                print(f"Ожидание загрузки новой страницы (задержка {delay_between_pages} сек)...")
                time.sleep(delay_between_pages)

                try:
                    wait.until(EC.staleness_of(old_html_element))
                    print("Обнаружено обновление страницы (staleness_of).")
                except TimeoutException:
                    print("Предупреждение: Не удалось подтвердить обновление страницы через staleness_of.")

            except (NoSuchElementException, TimeoutException):
                print("Не удалось найти кнопку 'Далее' или она неактивна/не кликабельна. Завершение пагинации.")
                break
            except StaleElementReferenceException:
                 print("Элемент кнопки 'Далее' устарел во время попытки клика. Возможно, страница обновилась сама. Повторная попытка на следующей итерации...")
                 continue
            except Exception as e:
                print(f"Произошла непредвиденная ошибка при пагинации: {e}")
                break

    def close(self):
        if self.driver:
            print("Закрытие WebDriver...")
            self.driver.quit()
            self.driver = None
            print("WebDriver закрыт.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()