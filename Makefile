PYTHON = python3

JSON_OUTPUT = avito_json/avito_items.json
DB_FILE = avito_notifier.db 

.PHONY: install parse notify all clean

install:
	@echo "Установка зависимостей из requirements.txt..."
	$(PYTHON) -m pip install -r requirements.txt

scrape:
	@echo "Запуск парсера Avito..."
	$(PYTHON) scraper.py

parse:
	@echo "Запуск парсера Avito..."
	$(PYTHON) parser.py

notify: $(JSON_OUTPUT)
	@echo "Запуск отправки уведомлений в Telegram..."
	$(PYTHON) send_avito_notifications.py

all: notify

clean:
	@echo "Очистка сгенерированных файлов..."
	rm -f $(JSON_OUTPUT) sent_items.log $(DB_FILE) 
	@echo "Очистка завершена."

$(JSON_OUTPUT):