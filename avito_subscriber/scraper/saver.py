from selenium.webdriver.common.by import By
from .config import ITEMS_CONTAINER_SELECTOR, ITEM_SELECTOR

# save_items_html - сохраняет HTML контейнера с объявлениями в файл
# _save_full_page_html - сохраняет полную HTML страницу

def save_items_html(driver, page_num, data_dir="data"):
    try:
        # Подготовка
        items_container = driver.find_element(By.CSS_SELECTOR, ITEMS_CONTAINER_SELECTOR)
        items_html = items_container.get_attribute("outerHTML")

        # Сохранение
        with open(f"{data_dir}/items_page_{page_num}.html", "w", encoding="utf-8") as f:
            f.write(items_html)

        items = driver.find_elements(By.CSS_SELECTOR, ITEM_SELECTOR)
        print(f"Найдено и сохранено {len(items)} объявлений на странице {page_num}")
        
        return len(items)
        
    except Exception as e:
        print(f"Ошибка при сохранении HTML: {e}")
        return 0


def _save_full_page_html(driver, page_num, data_dir):
    full_page_html = driver.page_source
    with open(
        f"{data_dir}/full_page/items_page_{page_num}.html",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(full_page_html) 