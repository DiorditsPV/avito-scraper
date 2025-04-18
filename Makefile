PYTHON = python3

JSON_OUTPUT = avito_json/avito_items.json
DB_FILE = avito_notifier.db 

.PHONY: install parse notify all clean

install:
	@echo "Установка зависимостей из requirements.txt..."
	$(PYTHON) -m pip install -r requirements.txt

scrape:
	@echo "Запуск парсера Avito..."
	$(PYTHON) main/scraper.py

parse:
	@echo "Запуск парсера Avito..."
	$(PYTHON) main/parser.py

notify: $(JSON_OUTPUT)
	@echo "Запуск отправки уведомлений в Telegram..."
	$(PYTHON) main/notify.py

all: notify

clean:
	@echo "Очистка сгенерированных файлов..."
	rm -f $(JSON_OUTPUT) sent_items.log $(DB_FILE) 
	@echo "Очистка завершена."

$(JSON_OUTPUT):