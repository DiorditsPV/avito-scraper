import sqlite3
import os
from typing import Set

DEFAULT_DB_PATH = "db/avito_notifier.db"

class DatabaseClient:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        try:
            self.conn = sqlite3.connect(self.db_path)
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
            self.conn.commit()
            print("Таблица 'sent_items' проверена/создана.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы 'sent_items': {e}")

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
            return self.conn.total_changes > 0 or self.is_item_sent(item_id)
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении item_id='{item_id}': {e}")
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

    def close(self):
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                print(f"Соединение с базой данных {self.db_path} закрыто.")
            except sqlite3.Error as e:
                print(f"Ошибка при закрытии соединения с БД: {e}")