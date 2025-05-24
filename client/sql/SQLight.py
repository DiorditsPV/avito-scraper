import sqlite3
import os
import json
from typing import Dict, Any, List
from client.sql.config import DEFAULT_DB_PATH, DB_CONNECTION_SETTINGS
from client.sql.schema import *

class DatabaseClient:
    """
    SQLite клиент для работы с базой данных
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        self.connect()
        
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            print(f"Создана директория для базы данных: {self.db_path}")

        if not self.conn:
            raise Exception("Не удалось подключиться к базе данных. Загрузка в БД отменена.")
    
    #  --------BASE--------
    def connect(self):
        """Подключение к SQLite базе данных"""
        try:
            self.conn = sqlite3.connect(self.db_path, **DB_CONNECTION_SETTINGS)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"Подключение к базе данных {self.db_path} установлено")
        except Exception as e:
            print(f"Ошибка при подключении к БД ({self.db_path}): {e}")
            raise
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                print(f"Соединение с базой данных {self.db_path} закрыто.")
            except Exception as e:
                print(f"Ошибка при закрытии соединения с БД: {e}")

    def close(self):
        """Закрывает соединение с базой данных"""
        self.disconnect()
    
    #  --------SYSTEM TABLES----------------

    # def _initialize_tables(self):
    #     """Инициализирует основные таблицы"""
    #     ddl = get_items_table_ddl(table_name)
    #     success = self.execute_ddl(ddl)

    #     if not success:
    #         raise Exception("Ошибка при инициализации таблицы items")
        
    #     success = self.execute_ddl(SENT_ITEMS_TABLE_DDL)
    #     if not success:
    #         raise Exception("Ошибка при инициализации таблицы sent_items")


    def create_category_table(self, category_name: str):
        """
        Создает таблицу для конкретной категории
        """
        table_name = generate_category_table_name(category_name)
        ddl = get_items_table_ddl(table_name)
        success = self.execute_ddl(ddl)
        
        if not success:
            raise Exception(f"Ошибка при создании таблицы {table_name}")
            
    #  ---------EXECUTE---------------
    def execute_ddl(self, ddl_sql: str) -> bool:
        """
        Выполнение DDL команд 
        """
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return False
        
        try:
            self.cursor.execute(ddl_sql)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении DDL: {e}")
            return False
    
    def execute_query(self, sql: str, params: tuple = None) -> Any:
        """
        Выполнение SQL запросов
        """
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return None
        
        try:
            if params:
                return self.cursor.execute(sql, params)
            else:
                return self.cursor.execute(sql)
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None
        
    #  ---------ADD/UPDATE---------------
    
    def add_or_update_item(self, item_data, table_name = "items") -> bool:
        """
        Добавляет или обновляет объявление
        """
        if not self.cursor or not self.conn:
            print("Ошибка: база данных не инициализирована.")
            return False
        
        values = self.prepare_item_data(item_data)
        sql = get_upsert_sql(table_name)
        
        try:
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении/обновлении объявления: {e}")
            return False
    
    def add_or_update_item_to_category(self, category_name: str, item_data: Dict[str, Any]) -> bool:
        """
        Добавляет или обновляет запись в таблице категории
        """
        safe_table_name = generate_category_table_name(category_name)
        
        # Создаем таблицу если она не существует
        if not self.create_category_table(category_name):
            return False
        
        return self.add_or_update_item(item_data, safe_table_name)
    
    def prepare_item_data(self, item_data: Dict[str, Any]) -> List[Any]:
        """
        Подготавливает данные объявления для вставки в БД
        """
        values = []
        for col in ITEM_COLUMNS:
            value = item_data.get(col)
            if col in JSON_COLUMNS and value is not None:
                try:
                    values.append(json.dumps(value, ensure_ascii=False))
                except TypeError as e:
                    print(f"Ошибка сериализации JSON для колонки '{col}': {e}. Сохраняем как NULL.")
                    values.append(None)
            else:
                values.append(value)
        return values

    #  ---------NOTIFICATIONS---------------

    # def is_item_sent(self, item_id: str) -> bool:
    #     """
    #     Проверяет, было ли отправлено уведомление для объявления
    #     """
    #     if not self.cursor:
    #         print("Ошибка: курсор базы данных не инициализирован.")
    #         return False
        
    #     try:
    #         self.cursor.execute("SELECT 1 FROM sent_items WHERE item_id = ?", (item_id,))
    #         return self.cursor.fetchone() is not None
    #     except sqlite3.Error as e:
    #         print(f"Ошибка при проверке item_id='{item_id}': {e}")
    #         return False
    
    # def add_sent_item(self, item_id: str) -> bool:
    #     """
    #     Добавляет запись об отправленном уведомлении
    #     """
    #     if not self.cursor:
    #         print("Ошибка: курсор базы данных не инициализирован.")
    #         return False
        
    #     try:
    #         self.cursor.execute("INSERT OR IGNORE INTO sent_items (item_id) VALUES (?)", (item_id,))
    #         self.conn.commit()
    #         return self.is_item_sent(item_id)
    #     except sqlite3.Error as e:
    #         print(f"Ошибка при добавлении item_id='{item_id}' в sent_items: {e}")
    #         return False
    
    # def get_all_sent_items(self) -> Set[str]:
    #     """
    #     Возвращает все ID отправленных объявлений 
    #     """
    #     if not self.cursor:
    #         print("Ошибка: курсор базы данных не инициализирован.")
    #         return set()
        
    #     try:
    #         self.cursor.execute("SELECT item_id FROM sent_items")
    #         rows = self.cursor.fetchall()
    #         return set(row[0] for row in rows)
    #     except sqlite3.Error as e:
    #         print(f"Ошибка при получении всех отправленных item_id: {e}")
    #         return set()
# Для обратной совместимости

if __name__ == "__main__":
    db_client = DatabaseClient("data/test_db.db")
    db_client.create_category_table("test_category")