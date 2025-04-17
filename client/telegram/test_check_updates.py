import os
import sys
from dotenv import load_dotenv

# Добавляем корневую директорию проекта в sys.path
# Чтобы можно было импортировать client.telegram.tg
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) 
sys.path.insert(0, project_root)

from client.telegram.tg import TelegramNotifier

def main():
    # Загружаем переменные окружения из .env файла в корне проекта
    load_dotenv(override=True)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    print(bot_token)

    if not bot_token:
        print("Ошибка: Не задан TELEGRAM_BOT_TOKEN в .env файле")
        exit(1)

    # Создаем экземпляр без chat_id, так как он не нужен для получения обновлений
    notifier = TelegramNotifier(bot_token=bot_token)
    print("Получение информации об обновлениях...")
    notifier.get_updates_and_print_info()

if __name__ == "__main__":
    main() 