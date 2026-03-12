from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", "YOUR_ADMIN_CHAT_ID"))
    
    # Пути для сохранения файлов сессии
    SESSION_DIR: str = "sessions"
    LOG_FILE: str = "bot_logs.txt"

settings = Settings()
