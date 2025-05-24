import logging
import os
from typing import Optional, Literal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_directory(dir_type: Optional[Literal['raw', 'parsed']] = None) -> tuple[str, str]:
    try:
        raw_dirs = [d for d in os.listdir(f"data/{dir_type}") if os.path.isdir(os.path.join(f"data/{dir_type}", d))]
        if not raw_dirs:
            raise FileNotFoundError(f"Директория data/{dir_type} пуста")
        latest_dir = sorted(raw_dirs)[-1]
        time_marker, name_marker = latest_dir.split("_")[:2], latest_dir.split("_")[2:]
        logging.info(f"Используется последняя доступная директория: {latest_dir}")
        logging.info(f"time_marker: {time_marker}, name_marker: {name_marker}")
        return '_'.join(time_marker), '_'.join(name_marker)
    except FileNotFoundError as e:
        logging.error(f"Ошибка при поиске директории: {e}")
        raise