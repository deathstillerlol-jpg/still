import aiosqlite
from config import settings

class Database:
    def __init__(self):
        self.db_path = "bot_db.sqlite"

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    session_data TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            await db.commit()
            print("База данных успешно создана")

    async def add_user(self, user_id, username, session_token):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO users (user_id, username, session_data) VALUES (?, ?, ?)",
                (user_id, username, session_token)
            )
            await db.commit()

    async def get_user_sessions(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cursor:
                return await cursor.fetchone()
