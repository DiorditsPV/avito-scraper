import json
import os
import logging
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Dict, Any, List
from .utils import get_latest_directory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Селекторы для парсинга элементов объявления
SELECTORS = {
    "title": "a[data-marker='item-title']",
    "item_link": "a[data-marker='item-title']",
    "seller_link": [
        "a[href*='/brands/']",
        "a[href*='/user/']",
        ".style-root-Dh2i5 a"
    ],
    "item_id": "div[data-marker='item']",
    "price_marker": "p[data-marker='item-price']",
    
    "description": "div[data-marker='item'] > meta", # div.iva-item-bottomBlock-VewGa p.styles-module-margin-bottom_4-OpB5i
    "published_date": "p[data-marker='item-date']",
    "state": "div.iva-item-autoParamsStep-QxatK > p[data-marker='item-specific-params']",

    "seller_reviews": "p[data-marker='seller-info/summary']",
    "seller_name": "div[data-marker='seller-info/name']",
    "seller_rating": "span[data-marker='seller-info/score']",
    
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

    
    text = soup.select_one(SELECTORS["description"]).attrs.get('content') if soup.select_one(SELECTORS["description"]) else ''
    data["data"]["description"] = re.sub(r'\s+', ' ', text)


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
    
    item_id = soup.select_one(SELECTORS["item_id"]).get("data-item-id")
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

def parse_html(time_marker=None):
    if time_marker is None:
        time_marker, name_marker = get_latest_directory(dir_type='raw')

    data_dir = f"data/raw/{time_marker}_{name_marker}"
    output_dir = f"data/parsed/{time_marker}_{name_marker}"
    output_file = f"avito_items_{time_marker}_{name_marker}.json"
    
    os.makedirs(output_dir, exist_ok=True)
    
    html_files = [f for f in os.listdir(data_dir) if f.endswith('.html')]
    logging.info(f"Найдено {len(html_files)} HTML-файлов для парсинга")
    
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
                    if not item_data.get("data"):
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
    

def main():
    parse_html()
    

if __name__ == "__main__":
    main()
