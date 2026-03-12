import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import settings
from handlers import router
from database import Database

logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    database = Database()
    
    await database.init_db()
    
    try:
        await bot.start_polling(dp)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
