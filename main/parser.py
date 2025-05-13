import os
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
from client.sql.SQLight import DatabaseClient
import logging
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def print_selectors_summary(data_dir, html_file):
    """Выводит статистику по найденным селекторам в HTML-файле"""
    file_path = os.path.join(data_dir, html_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    logging.info("\n=== Саммари по селекторам ===")
    for selector_name, selector in SELECTORS.items():
        if isinstance(selector, list):
            total = sum(len(soup.select(s)) for s in selector)
            logging.info(f"{selector_name}: найдено {total} элементов (составной селектор)")
        else:
            count = len(soup.select(selector))
            logging.info(f"{selector_name}: найдено {count} элементов")
    logging.info("===========================\n")

# Селекторы для парсинга элементов объявления
SELECTORS = {
    "title": "a[data-marker='item-title']",
    "item_link": "a[data-marker='item-title']",
    "seller_link": [
        "a[href*='/brands/']",
        "a[href*='/user/']",
        ".style-root-Dh2i5 a"
    ],
    "price_marker": "p[data-marker='item-price']",
    
    "description": "div[data-marker='item']", # div.iva-item-bottomBlock-VewGa p.styles-module-margin-bottom_4-OpB5i
    "published_date": "p[data-marker='item-date']",
    "state": "div.iva-item-autoParamsStep-QxatK > p[data-marker='item-specific-params']",
    "seller_reviews": "p[data-marker='seller-info/summary']",
    "seller_name": "div[data-marker='seller-info/name']",
    "seller_rating": "div[data-marker='seller-info/score']",
    "location": "div[data-marker='item-address']",
    "date": "div[data-marker='item-date']",
    "item_container": "div[data-marker='item']",
    "params_container": "div[data-marker='item-params'] > div",

    "badge_container": "div.SnippetLayout-root-zT1oI", # мусор?
    "badge_title": "span.SnippetBadge-title-NCaUc",  # мусор?
}

def extract_item_data(item_html):
    soup = BeautifulSoup(item_html, 'html.parser')
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "data": {}
    }
    
    title_elem = soup.select_one(SELECTORS["title"])
    if title_elem:
        data["data"]["title"] = title_elem.get_text(strip=True)
        item_url = title_elem.get('href')
        if item_url:
            data["data"]["url"] = f"https://avito.ru{item_url}"
    
    if "url" not in data["data"]:
        link_elem = soup.select_one(SELECTORS["item_link"]) 
        if link_elem:
            item_url = link_elem.get('href')
            if item_url:
                data["data"]["url"] = f"https://avito.ru{item_url}"
    
    seller_link = None
    for selector in SELECTORS["seller_link"]:
        seller_link = soup.select_one(selector)
        if seller_link:
            break
            
    data["data"]["seller_url"] = None
    if seller_link:
        seller_url = seller_link.get('href').replace("?src=search_seller_info", "")
        data["data"]["seller_url"] = f"https://avito.ru{seller_url}" 
            

    if soup.select_one(SELECTORS["price_marker"]):
        price_elem = soup.select_one(SELECTORS["price_marker"])
        price_text = price_elem.get_text(strip=True)
        price_value = re.sub(r'[^\d]', '', price_text)
        data["data"]["price"] = int(price_value) if price_value else None
        data["data"]["price_text"] = price_text.replace('\xa0', ' ')
        
    description_elem = soup.select_one(SELECTORS["description"]) 
    if description_elem:
        data["data"]["description"] = re.sub(r'\s+', ' ', description_elem.get_text(strip=True))
    
    published = soup.select_one(SELECTORS["published_date"]) 
    if published:
        data["data"]["phone_state"] = published.get_text(strip=True)
    
    state = soup.select_one(SELECTORS["state"]) 
    if state:
        data["data"]["state"] = state.get_text(strip=True)
    
    badges = []
    for badge_elem in soup.select(SELECTORS["badge_container"]):
        badge_title = badge_elem.select_one(SELECTORS["badge_title"])
        if badge_title:
            badges.append(badge_title.get_text(strip=True))
    
    if badges:
        data["data"]["badges"] = badges
    
    reviews_elem = soup.select_one(SELECTORS["seller_reviews"])
    if reviews_elem:
        reviews_text = reviews_elem.get_text(strip=True)
        reviews_count_match = re.search(r'(\d+)', reviews_text)
        if reviews_count_match:
            data["data"]["seller_reviews_count"] = int(reviews_count_match.group(1))
        data["data"]["seller_reviews_text"] = reviews_text
    
    location_elem = soup.select_one(SELECTORS["location"])
    if location_elem:
        data["data"]["location"] = location_elem.get_text(strip=True)
    
    date_elem = soup.select_one(SELECTORS["date"])
    if date_elem:
        data["data"]["date"] = date_elem.get_text(strip=True)
    
    item_id = None
    if soup.has_attr('data-item-id'):
        item_id = soup['data-item-id']
    else:
        for elem in soup.select("[data-item-id]"):
            item_id = elem.get('data-item-id')
            if item_id:
                break
    
    if not item_id:
        for a_elem in soup.select(SELECTORS["item_link"]):
            href = a_elem.get('href', '')
            id_match = re.search(r'/item/([^/]+)', href)
            if id_match:
                item_id = id_match.group(1)
                break
    
    if item_id:
        data["data"]["item_id"] = item_id
    
    image_urls = []
    for img in soup.select("img[src*='/items/']"):
        src = img.get('src')
        if src:
            if '/' in src:
                src = src.split('/')[-1]
            image_urls.append(f"https://00.img.avito.st/image/{src}")
    
    data["data"]["images"] = image_urls
    
    params = {}
    for param_elem in soup.select(SELECTORS["params_container"]):
        param_text = param_elem.get_text(strip=True)
        if ":" in param_text:
            key, value = param_text.split(":", 1)
            params[key.strip()] = value.strip()
    
    if params:
        data["data"]["params"] = params
    
    seller_name = soup.select_one(SELECTORS["seller_name"])
    if seller_name:
        data["data"]["seller_name"] = seller_name.get_text(strip=True)
    
    seller_rating = soup.select_one(SELECTORS["seller_rating"])
    if seller_rating:
        rating_text = seller_rating.get_text(strip=True)
        data["data"]["seller_rating"] = rating_text
    
    return data

def get_latest_directory(dir_type: Optional[Literal['raw', 'parsed']] = None) -> tuple[str, str]:
    try:
        raw_dirs = [d for d in os.listdir(f"data/{dir_type}") if os.path.isdir(os.path.join(f"data/{dir_type}", d))]
        if not raw_dirs:
            raise FileNotFoundError(f"Директория data/{dir_type} пуста")
        latest_dir = sorted(raw_dirs)[-1]
        time_marker, name_marker = latest_dir.split("_")[:2], latest_dir.split("_")[2:]
        logging.info(f"Используется последняя доступная директория: {latest_dir}")
        logging.info(f"time_marker: {time_marker}, name_marker: {name_marker}")
        return '_'.join(time_marker), '_'.join(name_marker)
    except FileNotFoundError as e:
        logging.error(f"Ошибка при поиске директории: {e}")
        raise

def parse_html(time_marker=None):
    if time_marker is None:
        time_marker, name_marker = get_latest_directory(dir_type='raw')

    data_dir = f"data/raw/{time_marker}_{name_marker}"
    output_dir = f"data/parsed/{time_marker}_{name_marker}"
    output_file = f"avito_items_{time_marker}_{name_marker}.json"
    
    os.makedirs(output_dir, exist_ok=True)
    
    html_files = [f for f in os.listdir(data_dir) if f.endswith('.html')]
    logging.info(f"Найдено {len(html_files)} HTML-файлов для парсинга")
    
    if html_files:            
        print_selectors_summary(data_dir, html_files[0])
    
    total_items = 0
    all_items_data = []
    
    for html_file in html_files:
        file_path = os.path.join(data_dir, html_file)
        logging.info(f"Начало обработки файла: {html_file}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            items = soup.select(SELECTORS["item_container"])
            
            logging.info(f"В файле {html_file} найдено {len(items)} объявлений")
            
            for i, item in enumerate(items):
                item_id_attr = item.get('data-item-id') or item.get('id', f"unknown_item_{i}")
                try:
                    item_data = extract_item_data(str(item))

                    extracted_item_id = item_data.get("data", {}).get("item_id")
                    if not extracted_item_id:
                         logging.warning(f"Не удалось извлечь item_id из блока (атрибут блока: {item_id_attr}). Пропускаем.")
                         continue

                    all_items_data.append(item_data)
                    total_items += 1

                except Exception as e:
                    logging.error(f"Ошибка при обработке объявления (атрибут блока: {item_id_attr}) в файле {html_file}: {e}", exc_info=True) # Добавляем traceback
            
        except Exception as e:
            logging.error(f"Критическая ошибка при обработке файла {html_file}: {e}", exc_info=True)
    
    output_path = os.path.join(output_dir, output_file)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_items_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Парсинг завершен. Всего извлечено {total_items} объявлений.")
        logging.info(f"Данные сохранены в JSON файл: {output_path}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении JSON файла {output_path}: {e}", exc_info=True)
    

def load_parsed_in_db(time_marker=None, name_marker=None):
    if time_marker is None:
        time_marker, name_marker = get_latest_directory(dir_type='parsed')

    data_dir = f"data/parsed/{time_marker}_{name_marker}"
    json_file_path = os.path.join(data_dir, f"avito_items_{time_marker}_{name_marker}.json")
    db_client = None # Инициализируем None для блока finally
    inserted_count = 0
    inserted_category_count = 0

    logging.info("Начало загрузки данных из JSON в базу данных.")

    if not os.path.exists(json_file_path):
        logging.error(f"JSON файл не найден: {json_file_path}. Загрузка в БД отменена.")
        return

    try:
        db_client = DatabaseClient() # Использует путь по умолчанию 'db/avito_notifier.db'
        if not db_client.conn:
            logging.error("Не удалось подключиться к базе данных. Загрузка в БД отменена.")
            return

        # Создаем новую таблицу для категории, если есть name_marker
        if name_marker:
            logging.info(f"Создание таблицы для категории: {name_marker}")
            if not db_client.create_category_table(name_marker):
                logging.error(f"Не удалось создать таблицу для категории {name_marker}. Продолжаем загрузку только в общую таблицу.")

        with open(json_file_path, 'r', encoding='utf-8') as f:
            all_items_data = json.load(f)

        logging.info(f"Загружено {len(all_items_data)} записей из {json_file_path}.")

        for item_entry in all_items_data:
            item_data = item_entry.get("data", {})
            parsed_at = item_entry.get("timestamp")

            if not item_data or "item_id" not in item_data:
                logging.warning(f"Пропущена запись без 'data' или 'item_id': {item_entry}")
                continue

            # Формируем плоский словарь для передачи в БД
            flat_item = {
                "item_id": item_data.get("item_id"),
                "parsed_at": parsed_at,
                "title": item_data.get("title"),
                "price": item_data.get("price"),
                "price_text": item_data.get("price_text"),
                "url": item_data.get("url"),
                "seller_url": item_data.get("seller_url"),
                "description": item_data.get("description"),
                "published_date_text": item_data.get("date"), # Переименовали ключ для БД
                "phone_state": item_data.get("phone_state"),
                "condition": item_data.get("state"), # Переименовали ключ для БД
                "location": item_data.get("location"),
                "seller_name": item_data.get("seller_name"),
                "seller_rating": item_data.get("seller_rating"),
                "seller_reviews_count": item_data.get("seller_reviews_count"),
                "seller_reviews_text": item_data.get("seller_reviews_text"),
                "badges": item_data.get("badges"), # Передаем как есть, сериализация в db_client
                "images": item_data.get("images"), # Передаем как есть, сериализация в db_client
                "params": item_data.get("params")  # Передаем как есть, сериализация в db_client
            }
            
            # Добавляем в общую таблицу items
            if db_client.add_or_update_item(flat_item):
                inserted_count += 1 # Считаем все успешные операции
            else:
                logging.warning(f"Не удалось добавить/обновить объявление с ID: {flat_item['item_id']} в общую таблицу")
            
            # Добавляем в категорийную таблицу, если есть name_marker
            if name_marker:
                if db_client.add_or_update_item_to_category(name_marker, flat_item):
                    inserted_category_count += 1
                else:
                    logging.warning(f"Не удалось добавить/обновить объявление с ID: {flat_item['item_id']} в таблицу категории {name_marker}")

        logging.info(f"Загрузка в БД завершена. Успешно обработано {inserted_count} объявлений в общей таблице.")
        if name_marker:
            logging.info(f"В таблицу категории {name_marker} добавлено {inserted_category_count} объявлений.")

    except json.JSONDecodeError:
        logging.error(f"Ошибка декодирования JSON файла: {json_file_path}", exc_info=True)
    except Exception as e:
        logging.error(f"Ошибка во время загрузки данных в БД: {e}", exc_info=True)
    finally:
        if db_client:
            db_client.close()

def main():
    parse_html()
    load_parsed_in_db() # Добавляем вызов функции загрузки в БД
    

if __name__ == "__main__":
    main()