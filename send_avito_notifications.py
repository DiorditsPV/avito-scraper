import os
import json
import time
import argparse
from dotenv import load_dotenv
from client.telegram.tg import TelegramNotifier
from client.sql.SQLight import DatabaseClient

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JSON_FILE_PATH = "avito_json/avito_items.json"

def format_message(item_data):
    data = item_data.get("data", {})
    
    title = data.get("title", "Без названия")
    price = data.get("price_text", "Цена не указана")
    url = data.get("url", "Нет ссылки")
    location = data.get("location", "Местоположение не указано")
    date = data.get("date", "")
    description = data.get("description", "")
    
    if len(description) > 300:
        description = description[:300] + "..."
        
    def escape_markdown(text):
        if not isinstance(text, str):
             text = str(text)
        escape_chars = '_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in text)

    title_escaped = escape_markdown(title)
    price_escaped = escape_markdown(price)
    location_escaped = escape_markdown(location)
    date_escaped = escape_markdown(date)
    description_escaped = escape_markdown(description)
    url_escaped = url

    message = f"""
*{title_escaped}*

*Цена:* {price_escaped}
*Место:* {location_escaped}
*Дата:* {date_escaped}

{description_escaped}

[Посмотреть на Avito]({url_escaped})
    """
    return message.strip()


def main():


    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в .env файле.")
        return

    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    db_client = DatabaseClient()
    
    if not db_client.conn:
        print("Не удалось подключиться к базе данных. Завершение работы.")
        return

    if not os.path.exists(JSON_FILE_PATH):
        print(f"Ошибка: Файл {JSON_FILE_PATH} не найден.")
        db_client.close()
        return

    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            all_items_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {JSON_FILE_PATH}.")
        db_client.close()
        return
    except Exception as e:
        print(f"Ошибка при чтении файла {JSON_FILE_PATH}: {e}")
        db_client.close()
        return

    new_items_count = 0
    try:
        for item in all_items_data:
            item_id = item.get("data", {}).get("item_id")
            
            if not item_id:
                print("Предупреждение: Объявление без ID, пропускаем:", item.get("data", {}).get("title"))
                continue

            if not db_client.is_item_sent(item_id):
                message = format_message(item)
                try:
                    print(f"Отправка объявления: {item_id} - {item.get('data', {}).get('title')}")
                    response = notifier.send_message(message, parse_mode="MarkdownV2")
                    
                    if response.get("ok"):
                        if db_client.add_sent_item(item_id):
                            print(f"ID {item_id} добавлен в базу данных.")
                        else:
                            print(f"Предупреждение: не удалось добавить ID {item_id} в базу данных после отправки.")
                        new_items_count += 1
                        time.sleep(1)
                    else:
                        print(f"Ошибка отправки сообщения (MarkdownV2) для {item_id}. Ответ API: {response}. Попытка без форматирования...")
                        plain_message = message.replace('*', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                        response_plain = notifier.send_message(plain_message)
                        
                        if response_plain.get("ok"):
                            if db_client.add_sent_item(item_id):
                                print(f"ID {item_id} добавлен в базу данных (отправлено без форматирования).")
                            else:
                                print(f"Предупреждение: не удалось добавить ID {item_id} в базу данных после отправки (без форматирования).")
                            new_items_count += 1
                            print(f"Объявление {item_id} отправлено без форматирования.")
                            time.sleep(1)
                        else:
                            print(f"Ошибка повторной отправки сообщения (без форматирования) для {item_id}. Ответ API: {response_plain}")

                except Exception as e:
                    print(f"Критическая ошибка при отправке сообщения для {item_id}: {e}")

    finally:
        db_client.close()

    if new_items_count > 0:
        print(f"Отправлено {new_items_count} новых объявлений.")
    else:
        print("Новых объявлений для отправки не найдено.")

if __name__ == "__main__":
    main()