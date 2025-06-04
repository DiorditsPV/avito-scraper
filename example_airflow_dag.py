from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from avito_subscriber import AvitoScraper
from avito_subscriber.parser.parser import parse_html
from avito_subscriber.parser.loader import load_parsed_in_db
from avito_subscriber.scraper.config import SCRAPING_URLS

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def scrape_category(category_name: str, **context):
    """Скрейпинг конкретной категории товаров"""
    url = SCRAPING_URLS.get(category_name)
    if not url:
        raise ValueError(f"URL для категории {category_name} не найден")
    
    scraper = AvitoScraper(
        url_key=category_name,
        url=url,
        data_dir="data/raw",
        headless=True,
        max_pages=10
    )
    
    result = scraper.run()
    stats = scraper.get_stats()
    
    print(f"Скрейпинг завершен: {stats}")
    return result

def parse_scraped_data(**context):
    """Парсинг HTML данных в JSON"""
    dir_suffix = context['task_instance'].xcom_pull(task_ids='scrape')
    if not dir_suffix:
        raise ValueError("Не получен dir_suffix от задачи скрейпинга")
    
    time_marker = dir_suffix.split('_')[0]
    parse_html(time_marker)
    return dir_suffix

def load_to_database(**context):
    """Загрузка данных в базу данных"""
    dir_suffix = context['task_instance'].xcom_pull(task_ids='parse')
    if not dir_suffix:
        raise ValueError("Не получен dir_suffix от задачи парсинга")
    
    time_marker, name_marker = dir_suffix.split('_', 1)
    load_parsed_in_db(time_marker, name_marker)

# Создание DAG
dag = DAG(
    'avito_scraping_pipeline',
    default_args=default_args,
    description='Полный пайплайн скрейпинга Avito',
    schedule_interval=timedelta(hours=6),  # Запуск каждые 6 часов
    catchup=False,
    tags=['avito', 'scraping', 'etl'],
)

# Задача скрейпинга для MacBook Pro
scrape_task = PythonOperator(
    task_id='scrape',
    python_callable=scrape_category,
    op_kwargs={'category_name': 'macbook_pro'},
    dag=dag,
)

# Задача парсинга HTML в JSON
parse_task = PythonOperator(
    task_id='parse',
    python_callable=parse_scraped_data,
    dag=dag,
)

# Задача загрузки в БД
load_task = PythonOperator(
    task_id='load',
    python_callable=load_to_database,
    dag=dag,
)

# Определение зависимостей
scrape_task >> parse_task >> load_task

# Альтернативный DAG для нескольких категорий параллельно
dag_multi = DAG(
    'avito_multi_category_scraping',
    default_args=default_args,
    description='Скрейпинг нескольких категорий параллельно',
    schedule_interval=timedelta(days=1),  # Раз в день
    catchup=False,
    tags=['avito', 'scraping', 'parallel'],
)

categories = ['iphone_16_pro', 'mac_mini', 'kindle']

for category in categories:
    scrape_cat = PythonOperator(
        task_id=f'scrape_{category}',
        python_callable=scrape_category,
        op_kwargs={'category_name': category},
        dag=dag_multi,
    ) 