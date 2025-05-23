from src.notifier.tg import TelegramClient

class TelegramNotifier:
    def __init__(self, token=None, chat_id=None):
        self.telegram_client = TelegramClient(token, chat_id)
        
    def send_notification(self, message):
        """Отправляет уведомление через Telegram"""
        return self.telegram_client.send_message(message) 