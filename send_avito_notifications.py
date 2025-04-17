import os
import json
import time
from dotenv import load_dotenv
from client.telegram.tg import TelegramNotifier

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JSON_FILE_PATH = "avito_json/avito_items.json"
SENT_ITEMS_FILE = "sent_items.log"

def load_sent_items():
    if not os.path.exists(SENT_ITEMS_FILE):
        return set()
    try:
        with open(SENT_ITEMS_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"Ошибка при чтении файла {SENT_ITEMS_FILE}: {e}")
        return set()

def save_sent_item(item_id):
    try:
        with open(SENT_ITEMS_FILE, 'a') as f:
            f.write(f"{item_id}\n")
    except Exception as e:
        print(f"Ошибка при записи в файл {SENT_ITEMS_FILE}: {e}")

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

    if not os.path.exists(JSON_FILE_PATH):
        print(f"Ошибка: Файл {JSON_FILE_PATH} не найден.")
        return

    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    sent_items = load_sent_items()
    
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            all_items_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось прочитать JSON из файла {JSON_FILE_PATH}.")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла {JSON_FILE_PATH}: {e}")
        return

    new_items_count = 0
    for item in all_items_data:
        item_id = item.get("data", {}).get("item_id")
        
        if not item_id:
            print("Предупреждение: Объявление без ID, пропускаем:", item.get("data", {}).get("title"))
            continue

        if item_id not in sent_items:
            message = format_message(item)
            try:
                print(f"Отправка объявления: {item_id} - {item.get('data', {}).get('title')}")
                response = notifier.send_message(message, parse_mode="MarkdownV2")
                if response.get("ok"):
                    save_sent_item(item_id)
                    sent_items.add(item_id)
                    new_items_count += 1
                    time.sleep(1)
                else:
                    # Выводим полный ответ от API для диагностики
                    print(f"Ошибка отправки сообщения (MarkdownV2) для {item_id}. Ответ API: {response}. Попытка без форматирования...")
                    plain_message = message.replace('*', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                    response_plain = notifier.send_message(plain_message)
                    if response_plain.get("ok"):
                         save_sent_item(item_id)
                         sent_items.add(item_id)
                         new_items_count += 1
                         print(f"Объявление {item_id} отправлено без форматирования.")
                         time.sleep(1)
                    else:
                         # Выводим полный ответ от API для диагностики
                         print(f"Ошибка повторной отправки сообщения (без форматирования) для {item_id}. Ответ API: {response_plain}")

            except Exception as e:
                print(f"Критическая ошибка при отправке сообщения для {item_id}: {e}")
        else:
            pass

    if new_items_count > 0:
        print(f"Отправлено {new_items_count} новых объявлений.")
    else:
        print("Новых объявлений для отправки не найдено.")

if __name__ == "__main__":
    main()