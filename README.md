# Avito Scraper & Telegram Notifier

Скачивает HTML Avito (Selenium) -> Парсит -> SQLite + JSON -> Уведомления о новых в Telegram.

# **Что умеет сейчас:**

Предварительно нужно указтаь страницу парсинга - нужно вязть ссылку с  проставленными флагами, сортировкой и фильтрами. `main/scraper.py -> константа URL`

`make scrape`: Переходит по переменной URL и собирает все блоки объявлений, размещает в `'data/raw/<data_time>'`

`make parse`: Берет html из `'data/raw/`<data_time>`'` по последней метке времени и парсит в структуру, размещает структуру в `'avito_json/'`:

```
# item_id - id объявления
# parsed_at - дата и время парсинга
# title - название объявления
# price - цена
# price_text - текст цены
# url - url объявления
# seller_url - url продавца
# description - описание
# published_date_text - дата публикации
# phone_state - состояние телефона
# condition - состояние
# location - местоположение
# seller_name - имя продавца
# seller_rating - рейтинг продавца
# seller_reviews_count - количество отзывов
# seller_reviews_text - текст отзывов
# badges - метки
# images - изображения
# params - параметры
```

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
