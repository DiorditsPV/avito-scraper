# Определяем интерпретатор Python
PYTHON = python3

# Файлы и директории
JSON_OUTPUT = avito_json/avito_items.json

.PHONY: main parse send

# Основная цель
main: send

# Запуск парсера
parse:
	@echo "Запуск парсера Avito..."
	$(PYTHON) parser.py

# Отправка уведомлений
send: $(JSON_OUTPUT)
	@echo "Отправка уведомлений в Telegram..."
	$(PYTHON) send_avito_notifications.py

send_test:
	@echo "Отправка тестового сообщения в Telegram..."
	$(PYTHON) client/telegram/test_send_message.py

check_updates:
	@echo "Проверка обновлений в Telegram..."
	$(PYTHON) client/telegram/test_check_updates.py

$(JSON_OUTPUT):