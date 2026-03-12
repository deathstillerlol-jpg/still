# requirements.txt
# aiogram==3.13.* (или новее)
# telethon==1.* (лучше >=1.37)

import asyncio
import logging
from pathlib import Path
from typing import Dict

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# ──────────────────────────────────────────────
#  НАСТРОЙКИ — поменяй на свои
BOT_TOKEN = "8757500911:AAEbSh9hlRam0GYC1HdkoXCGTd9Q1vVBeNc"
API_ID = 31462757
API_HASH = "79ae4e151e84526e11b107e99ad67177"
OWNER_ID = 8559221549  # твой Telegram ID

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class AddSession(StatesGroup):
    phone = State()
    code = State()
    password = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("Доступ запрещён.")
        return
    await message.answer(
        "Привет! Используй /add чтобы добавить свой аккаунт.\n"
        "Все сессии сохраняются только локально в папке sessions/"
    )


@router.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        return
    await message.answer("Введи номер телефона в международном формате\nПример: +79123456789")
    await state.set_state(AddSession.phone)


@router.message(AddSession.phone, F.text)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith("+") or not phone[1:].isdigit():
        await message.answer("Неверный формат. Пример: +79123456789")
        return

    await state.update_data(phone=phone)

    # Создаём временного клиента
    session_name = f"session_{phone.replace('+', '').replace(' ', '')}"
    client = TelegramClient(
        StringSession(),  # сначала пустая сессия
        API_ID,
        API_HASH,
        connection_retries=None,
        retry_delay=1
    )

    await client.connect()

    try:
        sent = await client.send_code_request(phone)
        await state.update_data(
            phone_code_hash=sent.phone_code_hash,
            client=client,           # сохраняем клиента в FSM (не идеально, но для простоты)
            session_name=session_name
        )
        await message.answer(f"Код отправлен в Telegram.\nВведи код (5 цифр):")
        await state.set_state(AddSession.code)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        await state.clear()


@router.message(AddSession.code, F.text)
async def process_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client: TelegramClient = data["client"]
    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]
    session_name = data["session_name"]
    code = message.text.strip()

    try:
        await client.sign_in(
            phone=phone,
            code=code,
            phone_code_hash=phone_code_hash
        )

        # Успешный вход без 2FA
        session_str = client.session.save()
        save_session(session_name, session_str)
        await message.answer(f"Аккаунт {phone} успешно добавлен!\nСессия сохранена.")
        await client.disconnect()
        await state.clear()

    except SessionPasswordNeededError:
        await state.update_data(client=client)
        await message.answer("Включена двухфакторная аутентификация.\nВведи пароль 2FA:")
        await state.set_state(AddSession.password)

    except Exception as e:
        await message.answer(f"Ошибка при вводе кода: {e}")
        await client.disconnect()
        await state.clear()


@router.message(AddSession.password, F.text)
async def process_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client: TelegramClient = data["client"]
    session_name = data["session_name"]
    password = message.text.strip()

    try:
        await client.sign_in(password=password)
        session_str = client.session.save()
        save_session(session_name, session_str)
        await message.answer(f"Аккаунт успешно добавлен с 2FA!")
        await client.disconnect()
        await state.clear()

    except Exception as e:
        await message.answer(f"Неверный пароль или ошибка: {e}")
        await client.disconnect()
        await state.clear()


def save_session(name: str, session_str: str):
    path = SESSIONS_DIR / f"{name}.session"
    with open(path, "w", encoding="utf-8") as f:
        f.write(session_str)
    logging.info(f"Сессия сохранена: {path}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
