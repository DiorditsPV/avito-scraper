import sqlite3
import os
import json
from typing import Set, Dict, Any, Optional

DEFAULT_DB_PATH = "db/avito_notifier.db"

class DatabaseClient:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Создана директория для базы данных: {db_dir}")

        self.db_path = db_path
        self.conn = None
        self.cursor = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"Успешное подключение к базе данных: {self.db_path}")
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Ошибка при подключении или инициализации БД ({self.db_path}): {e}")

    def create_tables(self):
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return
            
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_items (
                item_id TEXT PRIMARY KEY,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id TEXT PRIMARY KEY,
                parsed_at TEXT,
                title TEXT,
                price INTEGER,
                price_text TEXT,
                url TEXT UNIQUE,
                seller_url TEXT,
                description TEXT,
                published_date_text TEXT,
                phone_state TEXT,
                condition TEXT,
                location TEXT,
                seller_name TEXT,
                seller_rating TEXT,
                seller_reviews_count INTEGER,
                seller_reviews_text TEXT,
                badges TEXT,  -- JSON string
                images TEXT, -- JSON string
                params TEXT, -- JSON string
                last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            self.conn.commit()
            print("Таблицы 'sent_items' и 'items' проверены/созданы.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    def is_item_sent(self, item_id: str) -> bool:
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return False
            
        try:
            self.cursor.execute("SELECT 1 FROM sent_items WHERE item_id = ?", (item_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Ошибка при проверке item_id='{item_id}': {e}")
            return False

    def add_sent_item(self, item_id: str) -> bool:
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return False
            
        try:
            self.cursor.execute("INSERT OR IGNORE INTO sent_items (item_id) VALUES (?)", (item_id,))
            self.conn.commit()
            return self.is_item_sent(item_id)
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении item_id='{item_id}' в sent_items: {e}")
            return False

    def get_all_sent_items(self) -> Set[str]:
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return set()
            
        try:
            self.cursor.execute("SELECT item_id FROM sent_items")
            rows = self.cursor.fetchall()
            return set(row[0] for row in rows)
        except sqlite3.Error as e:
            print(f"Ошибка при получении всех отправленных item_id: {e}")
            return set()

    def add_or_update_item(self, item_data: Dict[str, Any]) -> bool:
        if not self.cursor or not self.conn:
            print("Ошибка: база данных не инициализирована.")
            return False

        item_id = item_data.get("item_id")
        if not item_id:
            print("Ошибка: 'item_id' отсутствует в данных для добавления/обновления.")
            return False

        columns = [
            "item_id", "parsed_at", "title", "price", "price_text", "url",
            "seller_url", "description", "published_date_text", "phone_state",
            "condition", "location", "seller_name", "seller_rating",
            "seller_reviews_count", "seller_reviews_text", "badges", "images", "params"
        ]

        values = []
        for col in columns:
            value = item_data.get(col)
            if col in ["badges", "images", "params"] and value is not None:
                try:
                    values.append(json.dumps(value, ensure_ascii=False))
                except TypeError as e:
                    print(f"Ошибка сериализации JSON для колонки '{col}', item_id='{item_id}': {e}. Сохраняем как NULL.")
                    values.append(None)
            else:
                values.append(value)

        sql = f"""
        INSERT INTO items ({', '.join(columns)})
        VALUES ({', '.join('?'*len(columns))})
        ON CONFLICT(item_id) DO UPDATE SET
            parsed_at=excluded.parsed_at,
            title=excluded.title,
            price=excluded.price,
            price_text=excluded.price_text,
            url=excluded.url,
            seller_url=excluded.seller_url,
            description=excluded.description,
            published_date_text=excluded.published_date_text,
            phone_state=excluded.phone_state,
            condition=excluded.condition,
            location=excluded.location,
            seller_name=excluded.seller_name,
            seller_rating=excluded.seller_rating,
            seller_reviews_count=excluded.seller_reviews_count,
            seller_reviews_text=excluded.seller_reviews_text,
            badges=excluded.badges,
            images=excluded.images,
            params=excluded.params,
            last_updated_at=CURRENT_TIMESTAMP
        """

        try:
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении/обновлении item_id='{item_id}' в таблицу items: {e}")
            return False

    def close(self):
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                print(f"Соединение с базой данных {self.db_path} закрыто.")
            except sqlite3.Error as e:
                print(f"Ошибка при закрытии соединения с БД: {e}")