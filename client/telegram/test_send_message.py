import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) 
sys.path.insert(0, project_root)

from client.telegram.tg import TelegramNotifier

def main():
    # Загружаем переменные окружения из .env файла в корне проекта
    load_dotenv(override=True)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        print("Ошибка: Не задан TELEGRAM_BOT_TOKEN в .env файле")
        exit(1)
        
    if not chat_id:
        print("Ошибка: Не задан TELEGRAM_CHAT_ID в .env файле для отправки сообщения")
        exit(1)
        
    # Создаем экземпляр с указанием chat_id
    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id) 
    
    print(f"Отправка тестового сообщения в чат {chat_id}...")
    response = notifier.send_message("Тестовое сообщение от TelegramNotifier (test_send_message.py)")
    
    if response.get("ok"):
        print("Тестовое сообщение успешно отправлено!")
    else:
        print(f"Ошибка при отправке тестового сообщения: {response}")

if __name__ == "__main__":
    main() 