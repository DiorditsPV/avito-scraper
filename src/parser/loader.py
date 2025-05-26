import os
import json
from src.parser.utils import get_latest_directory
from src.client.sql.SQLight import DatabaseClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_parsed_in_db(time_marker=None, name_marker=None):        
    data_dir = f"data/parsed/{time_marker}_{name_marker}"
    json_file_path = os.path.join(data_dir, f"avito_items_{time_marker}_{name_marker}.json")
    inserted_category_count = 0

    logging.info("Начало загрузки данных из JSON в базу данных.")

    if not os.path.exists(json_file_path):
        logging.error(f"JSON файл не найден: {json_file_path}. Загрузка в БД отменена.")
        return

    try:
        db_client = DatabaseClient(name_marker=name_marker) 

        with open(json_file_path, 'r', encoding='utf-8') as f:
            all_items_data = json.load(f)

        logging.info(f"Загружено {len(all_items_data)} записей из {json_file_path}.")

        for item_entry in all_items_data:
            item_data = item_entry.get("data", {})
            parsed_at = item_entry.get("timestamp")

            if not item_data:
                logging.warning(f"Пропущена запись без 'data'")
                continue
            
            if "item_id" not in item_data:
                logging.warning(f"Пропущена запись без 'item_id'")
                continue

            # Формируем плоский словарь для передачи в БД
            flat_item = {
                "item_id": item_data.get("item_id"),
                "parsed_at": parsed_at,
                "title": item_data.get("title").lower() if item_data.get("title") else None,
                "price": item_data.get("price"),
                "price_text": item_data.get("price_text"),
                "url": item_data.get("url"),
                "seller_url": item_data.get("seller_url"),
                "description": item_data.get("description").lower() if item_data.get("description") else None,
                "published_date_text": item_data.get("date"), 
                "phone_state": item_data.get("phone_state"),
                "condition": item_data.get("state"),
                "location": item_data.get("location"),
                "seller_name": item_data.get("seller_name"),
                "seller_rating": item_data.get("seller_rating"),
                "seller_reviews_count": item_data.get("seller_reviews_count"),
                "seller_reviews_text": item_data.get("seller_reviews_text"),
                "badges": item_data.get("badges"),  
                "images": item_data.get("images"), 
                "params": item_data.get("params") 
            }
            
            # Добавляем в категорийную таблицу, если есть name_marker
            if db_client.upsert_item(flat_item):
                inserted_category_count += 1
            else:
                logging.warning(f"Не удалось добавить/обновить объявление с ID: {flat_item['item_id']} в таблицу категории {name_marker}")

        logging.info(f"Загрузка в БД завершена. Успешно обработано {inserted_category_count} объявлений в общей таблице.")


    except json.JSONDecodeError:
        logging.error(f"Ошибка декодирования JSON файла: {json_file_path}", exc_info=True)
    except Exception as e:
        logging.error(f"Ошибка во время загрузки данных в БД: {e}", exc_info=True)
    finally:
        if db_client:
            db_client.close()


def main():
    time_marker, name_marker = get_latest_directory(dir_type='parsed')
    load_parsed_in_db(time_marker, name_marker)
    

if __name__ == "__main__":
    main()