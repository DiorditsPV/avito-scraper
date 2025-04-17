import os
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_item_data(item_html):
    soup = BeautifulSoup(item_html, 'html.parser')
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "data": {}
    }
    
    title_elem = soup.select_one("a.styles-module-root-m3BML")
    if title_elem:
        data["data"]["title"] = title_elem.get_text(strip=True)
        item_url = title_elem.get('href')
        if item_url:
            data["data"]["url"] = f"https://avito.ru{item_url}"
    elif soup.select_one("h3.title-root"):
        data["data"]["title"] = soup.select_one("h3.title-root").get_text(strip=True)
    
    if "url" not in data["data"]:
        link_elem = soup.select_one("a[href*='/item/']") or soup.select_one("a[data-marker='item-title']")
        if link_elem:
            item_url = link_elem.get('href')
            if item_url:
                data["data"]["url"] = f"https://avito.ru{item_url}"
    
    seller_link = soup.select_one("a[href*='/brands/']") or soup.select_one("a[href*='/user/']") or soup.select_one(".style-root-Dh2i5 a")
    data["data"]["seller_url"] = None
    if seller_link:
        seller_url = seller_link.get('href').replace("?src=search_seller_info", "")
        data["data"]["seller_url"] = f"https://avito.ru{seller_url}" 
            
    price_container = soup.select_one("div.price-priceContent-kPm_N")
    if price_container:
        price_elem = price_container.select_one("span") or price_container.select_one("[data-marker='item-price']")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_value = re.sub(r'[^\d]', '', price_text)
            data["data"]["price"] = int(price_value) if price_value else None
            data["data"]["price_text"] = price_text.replace('\xa0', ' ')
    elif soup.select_one("span[data-marker='item-price']"):
        price_elem = soup.select_one("span[data-marker='item-price']")
        price_text = price_elem.get_text(strip=True)
        price_value = re.sub(r'[^\d]', '', price_text)
        data["data"]["price"] = int(price_value) if price_value else None
        data["data"]["price_text"] = price_text.replace('\xa0', ' ')
    
    description_elem = soup.select_one("div.iva-item-bottomBlock-FhNhY p.styles-module-ellipsis-A5gkK") 
    if description_elem:
        data["data"]["description"] = re.sub(r'\s+', ' ', description_elem.get_text(strip=True))
    
    published = soup.select_one('p[data-marker="item-date"]') 
    if published:
        data["data"]["phone_state"] = published.get_text(strip=True)
    
    state = soup.select_one('div.iva-item-autoParamsStep-QxatK > p[data-marker="item-specific-params"]') 
    if state:
        data["data"]["state"] = state.get_text(strip=True)
    
    badges = []
    for badge_elem in soup.select(".SnippetLayout-item-jLNdn"):
        badge_title = badge_elem.select_one(".SnippetBadge-title-DlcCS")
        if badge_title:
            badges.append(badge_title.get_text(strip=True))
    
    if badges:
        data["data"]["badges"] = badges
    
    reviews_elem = soup.select_one("p[data-marker='seller-info/summary']")
    if reviews_elem:
        reviews_text = reviews_elem.get_text(strip=True)
        reviews_count_match = re.search(r'(\d+)', reviews_text)
        if reviews_count_match:
            data["data"]["seller_reviews_count"] = int(reviews_count_match.group(1))
        data["data"]["seller_reviews_text"] = reviews_text
    
    location_elem = soup.select_one("div[data-marker='item-address']")
    if location_elem:
        data["data"]["location"] = location_elem.get_text(strip=True)
    
    date_elem = soup.select_one("div[data-marker='item-date']")
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
        for a_elem in soup.select("a[href*='/item/']"):
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
    for param_elem in soup.select("div[data-marker='item-params'] > div"):
        param_text = param_elem.get_text(strip=True)
        if ":" in param_text:
            key, value = param_text.split(":", 1)
            params[key.strip()] = value.strip()
    
    if params:
        data["data"]["params"] = params
    
    seller_name = soup.select_one("div[data-marker='seller-info/name']")
    if seller_name:
        data["data"]["seller_name"] = seller_name.get_text(strip=True)
    
    seller_rating = soup.select_one("div[data-marker='seller-rating']")
    if seller_rating:
        rating_text = seller_rating.get_text(strip=True)
        data["data"]["seller_rating"] = rating_text
    
    return data

def main():
    items_dir = "data/"
    output_dir = "avito_json"
    output_file = "avito_items.json"
    
    os.makedirs(output_dir, exist_ok=True)
    
    html_files = [f for f in os.listdir(items_dir) if f.endswith('.html')]
    print(f"Найдено {len(html_files)} HTML-файлов")
    
    total_items = 0
    all_items_data = []
    
    for html_file in html_files:
        file_path = os.path.join(items_dir, html_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            items = soup.select("div[data-marker='item']") or soup.select(".iva-item-root-Se7z4")
            
            print(f"В файле {html_file} найдено {len(items)} объявлений")
            
            for i, item in enumerate(items):
                try:
                    item_id = item.get('data-item-id') or item.get('id', f"item_{i}")
                    item_data = extract_item_data(str(item))
                    
                    if 'item_id' in item_data['data']:
                        item_id = item_data['data']['item_id']
                    
                    all_items_data.append(item_data)
                    
                    total_items += 1
                    print(f"Обработано объявление: {item_id}")
                except Exception as e:
                    print(f"Ошибка при обработке объявления в файле {html_file}: {e}")
            
        except Exception as e:
            print(f"Ошибка при обработке файла {html_file}: {e}")
    
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_items_data, f, ensure_ascii=False, indent=2)
    
    print(f"Извлечение данных завершено. Всего обработано {total_items} объявлений.")
    print(f"Все данные сохранены в файл: {output_path}")

if __name__ == "__main__":
    main() 