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
    def __init__(self, headless=True, remote_selenium_url=None):
        options = webdriver.ChromeOptions()
         
        critical_options = [
            '--headless',  # Всегда включаем headless в production
            '--no-sandbox',  # Критично для Docker
            '--disable-dev-shm-usage',  # Критично для Docker
            '--disable-gpu',
            '--window-size=1920,1080',
        ]

        # Опции для стабильности и производительности
        stability_options = [
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',  # Ускоряет загрузку
            '--disable-software-rasterizer',
            '--disable-features=VizDisplayCompositor',
            '--remote-debugging-port=9222',
        ]

        # Дополнительные настройки оптимизации
        optimization_options = [
            '--log-level=3',
            '--silent',
            '--disable-logging',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection'
        ]

        chrome_options = critical_options # + stability_options + optimization_options
        
        for option in chrome_options:
            options.add_argument(option)
        
        # User agent для избежания блокировки
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')

        try:
            if remote_selenium_url:
                # Используем удаленный Selenium Grid
                print(f"Подключение к удаленному Selenium: {remote_selenium_url}")
                self.driver = webdriver.Remote(command_executor=remote_selenium_url, options=options)
                print("WebDriver успешно подключен к удаленному Selenium Grid.")
            else:
                # Локальная инициализация (оригинальный код)
                # Диагностика: проверяем наличие Chrome/Chromium
                chrome_found = False
                try:
                    chrome_version = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
                    print(f"Chrome версия: {chrome_version.stdout.strip()}")
                    chrome_found = True
                except FileNotFoundError:
                    try:
                        chromium_version = subprocess.run(['chromium-browser', '--version'], capture_output=True, text=True)
                        print(f"Chromium версия: {chromium_version.stdout.strip()}")
                        options.binary_location = '/usr/bin/chromium-browser'
                        chrome_found = True
                    except FileNotFoundError:
                        print("ВНИМАНИЕ: Ни Google Chrome, ни Chromium не найдены в системе!")
                        print("Установите Chrome: apt-get install -y google-chrome-stable")
                        print("Или Chromium: apt-get install -y chromium-browser")
                
                # Попытка использовать системный chromedriver если есть
                system_chromedriver = '/usr/bin/chromedriver'
                if os.path.exists(system_chromedriver):
                    print(f"Используем системный ChromeDriver: {system_chromedriver}")
                    service = ChromeService(executable_path=system_chromedriver)
                else:
                    print("Загружаем ChromeDriver через webdriver-manager...")
                    service = ChromeService(executable_path=ChromeDriverManager().install())
                
                self.driver = webdriver.Chrome(service=service, options=options)
                print("WebDriver успешно инициализирован локально.")
            
        except Exception as e:
            print(f"Ошибка инициализации WebDriver: {e}")
            if not remote_selenium_url:
                print("\nВозможные решения:")
                print("1. Установите Chrome: apt-get update && apt-get install -y google-chrome-stable")
                print("2. Или установите Chromium: apt-get install -y chromium-browser")
                print("3. Установите зависимости: apt-get install -y libglib2.0-0 libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2")
                print("4. Проверьте права доступа к /dev/shm")
                print("5. Попробуйте установить ChromeDriver вручную: apt-get install -y chromium-chromedriver")
            else:
                print("Проверьте, что Selenium Grid доступен по адресу:", remote_selenium_url)
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