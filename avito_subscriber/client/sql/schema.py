# get_items_table_ddl - возвращает DDL для создания таблицы объявлений
# get_upsert_sql - возвращает SQL для операции UPSERT
# generate_category_table_name - возвращает имя таблицы для конкретной категории

def get_items_table_ddl(table_name: str = "items") -> str:
    return """
    CREATE TABLE IF NOT EXISTS {table_name} (
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
        images TEXT,  -- JSON string
        params TEXT,  -- JSON string
        last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """.format(table_name=table_name)


# Таблица для отслеживания отправленных уведомлений
SENT_ITEMS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS sent_items (
    item_id TEXT PRIMARY KEY,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# Схема колонок для операций вставки/обновления
ITEM_COLUMNS = [
    "item_id", "parsed_at", "title", "price", "price_text", "url",
    "seller_url", "description", "published_date_text", "phone_state",
    "condition", "location", "seller_name", "seller_rating",
    "seller_reviews_count", "seller_reviews_text", "badges", "images", "params"
]

# JSON поля для сериализации
JSON_COLUMNS = ["badges", "images", "params"]

# SQL шаблон для UPSERT операций
def get_upsert_sql(table_name: str = "items") -> str:
    columns = ', '.join(ITEM_COLUMNS)
    placeholders = ', '.join('?' * len(ITEM_COLUMNS))
    
    return """
    INSERT INTO {table_name} ({columns})
    VALUES ({placeholders})
    ON CONFLICT(item_id) DO UPDATE SET
        parsed_at            = excluded.parsed_at,
        title                = excluded.title,
        price                = excluded.price,
        price_text           = excluded.price_text,
        url                  = excluded.url,
        seller_url           = excluded.seller_url,
        description          = excluded.description,
        published_date_text  = excluded.published_date_text,
        phone_state          = excluded.phone_state,
        condition            = excluded.condition,
        location             = excluded.location,
        seller_name          = excluded.seller_name,
        seller_rating        = excluded.seller_rating,
        seller_reviews_count = excluded.seller_reviews_count,
        seller_reviews_text  = excluded.seller_reviews_text,
        badges               = excluded.badges,
        images               = excluded.images,
        params               = excluded.params,
        last_updated_at      = CURRENT_TIMESTAMP
    """.format(
            table_name=table_name,
            columns=columns,
            placeholders=placeholders
        )

def generate_category_table_name(category_name: str) -> str:
    safe_name = category_name.lower().replace('-', '_').replace(' ', '_')
    return f"category_{safe_name}" 