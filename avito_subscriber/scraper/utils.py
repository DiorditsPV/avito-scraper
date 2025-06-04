import os
import shutil
import glob
from datetime import datetime

# generate_data_directory - генерирует уникальное имя директории для хранения данных
# create_data_directory - создает директорию для хранения данных
# check_and_cleanup_directory - проверяет директорию и удаляет ее если она пуста

def generate_data_directory(base_dir, url_key):
    """
    Генерирует уникальное имя директории для хранения данных
    """
    timestamp_marker = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_suffix = f"{timestamp_marker}_{url_key}"
    data_dir = f"{base_dir}/{dir_suffix}"
    return data_dir, dir_suffix


def create_data_directory(data_dir):
    """
    Создает директорию для хранения данных
    """
    print(f"Создание директории для хранения данных: {data_dir}")
    os.makedirs(data_dir, exist_ok=True)


def check_and_cleanup_directory(data_dir):
    """
    Удаляет директорию если в ней нет файлов
    """
    try:
        if not os.path.exists(data_dir):
            return False
            
        files = glob.glob(os.path.join(data_dir, '*'))
        
        if not files:
            print(f"Директория {data_dir} пуста. Удаляем...")
            shutil.rmtree(data_dir)
            return False
            
        print(f"==> Директория {data_dir} содержит {len(files)} файлов. Сохраняем.")
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке директории {data_dir}: {e}")
        return False 