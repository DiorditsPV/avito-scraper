import requests
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: Optional[str] = None, chat_id: Optional[str] = None) -> Dict[str, Any]:
        target_chat_id = chat_id if chat_id else self.chat_id
        if not target_chat_id:
            return {"ok": False, "description": "Chat ID is not provided"}
            
        url = f"{self.api_url}/sendMessage"
        data = {
            "chat_id": target_chat_id,
            "text": text
        }
        if parse_mode:
            data["parse_mode"] = parse_mode
            
        response = requests.post(url, json=data)
        return response.json()

    def send_photo(self, photo_url: str, caption: Optional[str] = None, chat_id: Optional[str] = None) -> Dict[str, Any]:
        target_chat_id = chat_id if chat_id else self.chat_id
        if not target_chat_id:
            return {"ok": False, "description": "Chat ID is not provided"}
            
        url = f"{self.api_url}/sendPhoto"
        data = {
            "chat_id": target_chat_id,
            "photo": photo_url
        }
        if caption:
            data["caption"] = caption
            
        response = requests.post(url, json=data)
        return response.json()

    def send_document(self, document_url: str, caption: Optional[str] = None, chat_id: Optional[str] = None) -> Dict[str, Any]:
        target_chat_id = chat_id if chat_id else self.chat_id
        if not target_chat_id:
            return {"ok": False, "description": "Chat ID is not provided"}
            
        url = f"{self.api_url}/sendDocument"
        data = {
            "chat_id": target_chat_id,
            "document": document_url
        }
        if caption:
            data["caption"] = caption
            
        response = requests.post(url, json=data)
        return response.json()

    def get_updates_and_print_info(self, offset: Optional[int] = None, limit: int = 20) -> Dict[str, Any]:
        url = f"{self.api_url}/getUpdates"
        params = {"limit": limit}
        if offset:
            params["offset"] = offset
            
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            updates = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении обновлений: {e}")
            return {"ok": False, "description": str(e)}
        except json.JSONDecodeError:
            print("Ошибка: Не удалось декодировать JSON ответ от Telegram API.")
            return {"ok": False, "description": "JSON Decode Error"}

        if updates.get("ok"):
            print(f"Получено {len(updates.get('result', []))} обновлений:")
            last_update_id = None
            for update in updates.get("result", []):
                last_update_id = update.get("update_id")
                channel_post = update.get("channel_post")
                if channel_post:
                    chat = channel_post.get("chat", {})
                    chat_id = chat.get("id")
                    chat_title = chat.get("title", "<Без названия>")
                    chat_type = chat.get("type", "<Неизвестный тип>")
                    text = channel_post.get("text", "<Нет текста>")
                    print(f" - Чат ID: {chat_id}, Название: {chat_title}, Тип: {chat_type}, Сообщение: {text}")
                
            if last_update_id is not None:
                self.get_updates(offset=last_update_id + 1, limit=1)

        else:
            print(f"Ошибка при получении обновлений от Telegram: {updates.get('description')}")
        
        return updates
        
    def get_updates(self, offset: Optional[int] = None, limit: int = 1) -> Dict[str, Any]:
        url = f"{self.api_url}/getUpdates"
        params = {"limit": limit, "timeout": 5}
        if offset:
            params["offset"] = offset
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except requests.exceptions.RequestException:
            return {"ok": False, "description": "Request failed during update cleanup"}

if __name__ == "__main__":
    
    pass