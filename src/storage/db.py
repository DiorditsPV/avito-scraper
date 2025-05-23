class Storage:
    """Базовый класс для работы с хранилищем данных"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path
        
    def save_data(self, data, key=None):
        """Сохраняет данные в хранилище"""
        pass
        
    def load_data(self, key):
        """Загружает данные из хранилища"""
        pass
        
    def list_keys(self):
        """Возвращает список ключей в хранилище"""
        pass 