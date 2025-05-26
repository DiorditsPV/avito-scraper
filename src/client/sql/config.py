"""
Конфигурация для модуля storage
"""

# Настройки базы данных
DEFAULT_DB_PATH = "data/db/avito_notifier.db"

# Имена таблиц по умолчанию
DEFAULT_ITEMS_TABLE = "items"
DEFAULT_SENT_ITEMS_TABLE = "sent_items"

# Настройки подключения
DB_CONNECTION_SETTINGS = {
    "timeout": 30.0,
    "check_same_thread": False,
    "isolation_level": None  # autocommit mode
}

# Настройки для создания директорий
AUTO_CREATE_DB_DIR = True 