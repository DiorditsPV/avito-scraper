# Avito Scraper & Telegram Notifier

Скачивает HTML Avito (Selenium) -> Парсит -> SQLite + JSON -> Уведомления о новых в Telegram.

## Установка

1. Клонировать репо.
2. Создать venv: `python3 -m venv venv && source venv/bin/activate`
3. Установить зависимости: `make install` (или `pip install -r requirements.txt`)

   * *Примечание:* Для `scraper.py` (использующего Selenium) может потребоваться установка ChromeDriver или другого WebDriver и добавление его в PATH.
4. Создать `.env` файл и вписать свои Telegram Bot Token и Chat ID:

   ```dotenv
   TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
   TELEGRAM_CHAT_ID="YOUR_CHAT_ID_HERE"
   ```

   *(ID чата можно узнать через `python client/telegram/test_check_updates.py`)*

## Запуск

1. **(Опционально) Настроить URL и параметры** в `scraper.py` (URL поиска, количество страниц и т.д.).
2. **Скачать HTML-файлы:**

   ```bash
   make scrape
   # или
   # python scraper.py
   ```
   *(Сохранит HTML в `data/`)*
3. **Распарсить HTML и загрузить в БД:**

   ```bash
   make parse
   # или
   # python parser.py
   ```
   *(Создаст `avito_json/avito_items.json` и заполнит `db/avito_notifier.db`)*
4. **Отправить уведомления о новых:**

   ```bash
   make notify
   # или (команда по умолчанию)
   # make all
   ```
   *(Отправит только новые объявления)*
