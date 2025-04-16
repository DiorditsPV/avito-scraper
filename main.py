from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from client.selenium.selenium import SeleniumParser
import os

def main():
    URL = "https://www.avito.ru/moskva_i_mo/telefony/mobilnye_telefony/apple/iphone_16_pro-ASgBAgICA0SywA3KsYwVtMANzqs5sMENiPw3?cd=1"
    NEXT_BUTTON_LOCATOR = (By.CSS_SELECTOR, "li.next > a")
    
    ENABLE_PAGINATION = True
    MAX_PAGES = 3
    
    ITEMS_CONTAINER_SELECTOR = "div.items-items-Iy89l"
    ITEM_SELECTOR = "div.iva-item-root-Se7z4"
    
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    with SeleniumParser(headless=True) as parser:
        try:
            parser.go_to_page(URL)
            
            items_container = parser.wait_for_element(By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR, timeout=15)
            print("Контейнер с объявлениями загружен")
            
            items = parser.driver.find_elements(By.CSS_SELECTOR, ITEM_SELECTOR)
            print(f"Найдено {len(items)} объявлений на странице 1")
            
            parser.save_html(f"{data_dir}/page_1.html")
            
            total_items = len(items)
            
            if ENABLE_PAGINATION:
                print("\n--- Начало пагинации ---")
                page_num = 2
                
                for driver_instance in parser.handle_pagination(NEXT_BUTTON_LOCATOR[0], NEXT_BUTTON_LOCATOR[1], 
                                                             max_pages=MAX_PAGES, delay_between_pages=1.0):
                    items = driver_instance.find_elements(By.CSS_SELECTOR, ITEM_SELECTOR)
                    print(f"Найдено {len(items)} объявлений на странице {page_num}")
                    
                    parser.save_html(f"{data_dir}/page_{page_num}.html")
                    
                    total_items += len(items)
                    page_num += 1
                    print("-" * 10)
                
                print("--- Пагинация завершена ---")
            else:
                print("Пагинация отключена. Обработка только первой страницы.")
            
            print(f"\nВсего обработано {total_items} объявлений на {page_num-1} страницах")

        except TimeoutException:
            print("Не удалось загрузить страницу или найти контейнер с объявлениями.")
        except Exception as e:
            print(f"Произошла общая ошибка: {e}")

    print("\nРабота парсера завершена.")

if __name__ == "__main__":
    main()