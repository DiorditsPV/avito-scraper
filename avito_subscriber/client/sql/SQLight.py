import sqlite3
import os
import json
from typing import Dict, Any, List
from .config import DEFAULT_DB_PATH, DB_CONNECTION_SETTINGS
from .schema import *

# DatabaseClient
# -- __init__ - инициализирует соединение с базой данных
# -- connect - подключается к базе данных
# -- disconnect - отключается от базы данных
# -- close - закрывает соединение с базой данных
# -- execute_query - выполняет SQL запрос
# -- create_category_table - создает таблицу для конкретной категории

class DatabaseClient:
    """
    SQLite клиент для работы с базой данных
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH, name_marker: str = None):
        self.db_path = db_path
        self.category_name = generate_category_table_name(name_marker)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_category_table()

        # Создаем директорию для базы данных если она не существует
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Проверяем соединение с базой данных
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
            print(f"[ERROR] connect: {e}")
            raise
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
                print(f"Соединение с базой данных {self.db_path} закрыто.")
            except Exception as e:
                print(f"[ERROR] disconnect: {e}")

    def close(self):
        """Закрывает соединение с базой данных"""
        self.disconnect()

    #  ---------EXECUTE---------------
    
    def execute_query(self, sql: str, params: tuple = None) -> Any:
        """
        Выполнение SQL запросов
        """
        if not self.cursor:
            print("Ошибка: курсор базы данных не инициализирован.")
            return None
        try:
            return self.cursor.execute(sql, params) if params else self.cursor.execute(sql)
        except Exception as e:
            print(f"[ERROR] execute_query: {e}")
            return None
        
    #  --------SYSTEM TABLES----------------
    def create_category_table(self):
        """
        Создает таблицу для конкретной категории
        """
        ddl = get_items_table_ddl(self.category_name)
        success = self.execute_query(ddl)
        
        if not success:
            raise Exception(f"[ERROR] create_category_table")
            
    #  ---------UPDATE/INSERT---------------
    def upsert_item(self, item_data) -> bool:
        """
        Добавляет или обновляет объявление
        """
        values = self.prepare_item_data(item_data)
        sql = get_upsert_sql(self.category_name)
        
        try:
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] upsert_item: {e}")
            return False

    def prepare_item_data(self, item_data: dict) -> List[Any]:
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


if __name__ == "__main__":
    db_client = DatabaseClient("data/db/test_db.db", "test_category")
    db_client.create_category_table()
    db_client.upsert_item({
      "title": "MacBook Pro 13 m2 8gb 256gb",
      "url": "https://avito.ru/moskva/noutbuki/macbook_pro_13_m2_8gb_256gb_4838325978?slocation=107620&context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJxQk9adlVkUVY0UUlpeVN4Ijt9TRr9TT8AAAA",
      "seller_url": "https://avito.ru/brands/poturaev",
      "price": 72990,
      "price_text": "72 990₽",
      "description": "Bниmaниe. Дeйcтвует Aкция. Дoбрый день! Pады познaкомитьcя c Baми нa cтpанице нашeго мaгазинa! Пpедcтавляeм Bашему внимaнию. Арple macbооk pro 13 2022 m2 8gb 256gb. 256 GВ Ssd 8 GВ Rам. Цвeт: Space Gray. Aккумулятор: 75 Циклов. Все фото именно это",
      "badges": [
        "Надёжный продавец"
      ],
      "seller_reviews_count": 637,
      "seller_reviews_text": "637 отзывов",
      "item_id": "4838325978",
      "images": [],
      "seller_rating": "5,0"
    
  })
    db_client.close()


    