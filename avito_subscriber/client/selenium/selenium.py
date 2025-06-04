import time
import random
import os
import subprocess
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
        
        # Критически важные опции для Docker/контейнерной среды
        options.add_argument('--headless')  # Всегда включаем headless в production
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')  # Критично для Docker
        options.add_argument('--disable-dev-shm-usage')  # Критично для Docker
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Ускоряет загрузку
        
        # Дополнительные опции для стабильности в Docker
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--remote-debugging-port=9222')
        
        # Размер окна и прочие настройки
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # User agent для избежания блокировки
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

        try:
            # Диагностика: проверяем наличие Chrome
            try:
                chrome_version = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
                print(f"Chrome версия: {chrome_version.stdout.strip()}")
            except FileNotFoundError:
                print("ВНИМАНИЕ: Google Chrome не найден в системе!")
                print("Установите Chrome командой: apt-get install -y google-chrome-stable")
            
            # Попытка использовать системный chromedriver если есть
            system_chromedriver = '/usr/bin/chromedriver'
            if os.path.exists(system_chromedriver):
                print(f"Используем системный ChromeDriver: {system_chromedriver}")
                service = ChromeService(executable_path=system_chromedriver)
            else:
                print("Загружаем ChromeDriver через webdriver-manager...")
                service = ChromeService(executable_path=ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            print("WebDriver успешно инициализирован в headless режиме для Docker среды.")
            
        except Exception as e:
            print(f"Ошибка инициализации WebDriver: {e}")
            print("\nВозможные решения:")
            print("1. Установите Chrome: apt-get update && apt-get install -y google-chrome-stable")
            print("2. Установите зависимости: apt-get install -y libglib2.0-0 libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2")
            print("3. Проверьте права доступа к /dev/shm")
            print("4. Попробуйте установить ChromeDriver вручную: apt-get install -y chromium-chromedriver")
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
                wait = WebDriverWait(self.driver, 5)
                next_button = wait.until(
                    EC.element_to_be_clickable((next_button_locator_type, next_button_locator_value))
                )

                old_html_element = self.driver.find_element(By.TAG_NAME, "html")
                next_button.click()

                print(f"Ожидание загрузки новой страницы (задержка {delay_between_pages} сек)...")
                time.sleep(1)

                try:
                    wait.until(EC.staleness_of(old_html_element))
                    print("Обновление страницы (staleness_of).")
                except TimeoutException:
                    print("Предупреждение: Не удалось подтвердить обновление страницы через staleness_of.")

            except (NoSuchElementException, TimeoutException):
                print("Не удалось найти кнопку 'Далее'. Завершение пагинации.")
                break
            except StaleElementReferenceException:
                 print("Элемент кнопки 'Далее' устарел во время попытки клика. Возможно, страница обновилась сама. Повторная попытка на следующей итерации...")
                 continue
            except Exception as e:
                print(f"Произошла непредвиденная ошибка при пагинации: {e}")
                break

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()