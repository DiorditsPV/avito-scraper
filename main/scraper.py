from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from client.selenium.selenium import SeleniumParser
import os
from datetime import datetime
import time
URL = "https://www.avito.ru/moskva_i_mo/telefony/mobilnye_telefony/apple/iphone_16_pro-ASgBAgICA0SywA3KsYwVtMANzqs5sMENiPw3?cd=1&s=104&user=1"

MAX_PAGES = 15
WAIT_TIME = 8
PAGINATION_DELAY = 2.0
ITEMS_CONTAINER_SELECTOR = "div.items-items-zOkHg" # преодически меняется, нужно проверить по превфиксу - 'items-items-'
ITEM_SELECTOR = "div.iva-item-root-XBsVL" # тут проверить по префиксу - 'iva-item-root-'
NEXT_BUTTON_LOCATOR = (By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]')


def save_items_html(driver, page_num, save_full_page=False, data_dir="data"):
    try:
        if save_full_page:
            full_page_html = driver.page_source
            with open(
                f"{data_dir}/full_page/items_page_{page_num}.html",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(full_page_html)

        items_container = driver.find_element(By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR)
        items_html = items_container.get_attribute("outerHTML")

        with open(f"{data_dir}/items_page_{page_num}.html", "w", encoding="utf-8") as f:
            f.write(items_html)

        items = driver.find_elements(By.CSS_SELECTOR, ITEM_SELECTOR)
        print(f"Найдено и сохранено {len(items)} объявлений на странице {page_num}")
        print(
            f"Сохранены файлы: full_page_{page_num}_raw.html и items_page_{page_num}_container.html"
        )
        return len(items)
    except Exception as e:
        print(f"Ошибка при сохранении HTML: {e}")
        return 0


def scrape(enable_pagination=True):
    timestamp_marker=datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = f"data/raw/{timestamp_marker}"
    print(f"Создание директории для хранения данных: {data_dir}")
    os.makedirs(data_dir, exist_ok=True)

    with SeleniumParser(headless=True) as parser:
        try:
            parser.go_to_page(URL)
            time.sleep(5)
            parser.refresh_page()
            parser.wait_for_element(
                By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR, timeout=WAIT_TIME
            )
            print("Контейнер с объявлениями загружен")

            total_items = save_items_html(
                parser.driver, 1, save_full_page=False, data_dir=data_dir
            )

            if enable_pagination:
                print("\n--- Начало пагинации ---")
                page_num = 2

                for driver_instance in parser.handle_pagination(
                    NEXT_BUTTON_LOCATOR[0],
                    NEXT_BUTTON_LOCATOR[1],
                    max_pages=MAX_PAGES,
                    delay_between_pages=PAGINATION_DELAY,
                ):
                    items_count = save_items_html(
                        driver_instance,
                        page_num,
                        save_full_page=False,
                        data_dir=data_dir,
                    )
                    total_items += items_count
                    page_num += 1
                    print("-" * 10)

                print("--- Пагинация завершена ---")
            else:
                print("Пагинация отключена. Обработка только первой страницы.")

            print(
                f"\nВсего сохранено {total_items} объявлений на {page_num-1} страницах"
            )

        except TimeoutException:
            print("Не удалось загрузить страницу или найти контейнер с объявлениями.")
        except Exception as e:
            print(f"Произошла общая ошибка: {e}")

    print("\nРабота парсера завершена.")


def main():
    scrape()


if __name__ == "__main__":
    main()
