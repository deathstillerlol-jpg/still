from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from database import Database
from session_manager import SessionManager

router = Router()
db = Database()

@router.message(F.command_start)
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Я помогу вам создать безопасную сессию. "
        "Нажмите кнопку ниже для начала.",
        reply_markup={
            "inline_keyboard": [[{"text": "🔐 Создать сессию", "callback_data": "create_session"}]]
        }
    )

@router.callback_query(F.data == "create_session")
async def on_session_create(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    # Генерация сессии
    file_path, session_data = await SessionManager.generate_session_file(user_id, username)
    
    # Форматирование сообщения
    msg_text = SessionManager.format_session_for_telegram(session_data)
    
    # Отправка файла в чат
    file = FSInputFile(file_path)
    
    await callback.message.answer(
        msg_text,
        reply_markup=None
    )
    
    # Файл сессии как приложение (фича бота)
    await callback.message.answer_document(document=file)

    # Логирование для администратора
    await db.add_user(user_id, username, session_data['session_id'])
    
    # Отправка уведомления на Админ-чат
    # (В реальном проекте здесь будет логика отправки в канал)
    print(f"[Admin] Session {session_data['session_id']} successfully created.")
    
    await callback.answer("✅ Сессия успешно создана!")
