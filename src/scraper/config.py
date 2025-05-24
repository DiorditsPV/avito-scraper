from selenium.webdriver.common.by import By

# URL для скрейпинга различных категорий товаров
SCRAPING_URLS = {
    "iphone_16_pro": "https://www.avito.ru/moskva_i_mo/telefony/mobilnye_telefony/apple/iphone_16_pro-ASgBAgICA0SywA3KsYwVtMANzqs5sMENiPw3?cd=1&s=104&user=1",
    "mac_mini": "https://www.avito.ru/moskva_i_mo/nastolnye_kompyutery?cd=1&f=ASgBAgICAUTuvA2E0jQ&q=mac+mini&s=104&localPriority=1",
    "kindle": "https://www.avito.ru/moskva_i_mo/planshety_i_elektronnye_knigi/elektronnye_knigi-ASgBAgICAUSYAohO?cd=1&q=Amazon+kindle&s=104&localPriority=1",
    "macbook_pro": "https://www.avito.ru/moskva_i_mo/noutbuki/apple-ASgBAgICAUSo5A302WY?cd=1&f=ASgBAQICAUSo5A302WYBQJ7kDcTWzK0QpprGEJjNrRCOza0QkqPEEbKjxBGc2O8R1NjvEbDY7xHCmZYVqOOXFbyxnhU&q=macbook+pro&user=1"
}

# Настройки пагинации и тайминга
MAX_PAGES = 80
WAIT_TIME = 4.0

# CSS селекторы для элементов страницы
ITEMS_CONTAINER_SELECTOR = "div.items-items-zOkHg"  # периодически меняется, нужно проверить по префиксу - 'items-items-'
ITEM_SELECTOR = "div.iva-item-root-XBsVL"  # тут проверить по префиксу - 'iva-item-root-'

# Локатор кнопки "Следующая страница"
NEXT_BUTTON_LOCATOR = (By.CSS_SELECTOR, '[data-marker="pagination-button/nextPage"]')

# Настройки файлов и директорий
DEFAULT_DATA_DIR = "data/raw"
SAVE_FULL_PAGE = False 