from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from handlers.admin import get_admin_keyboard, ADMIN_IDS
from handlers.main_keyboard import get_main_keyboard
from services.db import AsyncDB

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "Добро пожаловать, админ! Вот ваша панель:",
            reply_markup=get_admin_keyboard()
        )
    else:
        keyboard = get_main_keyboard()
        await message.answer("Привет! Для регистрации используй /register.\nВыберите кнопку:", reply_markup=keyboard)

# Остальные команды ...

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/register — начать регистрацию\n"
        "/mydata — показать ваши зарегистрированные данные\n"
    )
    await message.answer(help_text)

@router.message(Command("mydata"))
async def cmd_mydata(message: Message, db: AsyncDB):
    user_id = message.from_user.id
    data = await db.get_registration(user_id)
    if data:
        await message.answer(
            f"Ваши данные:\n\n"
            f"ФИО: {data['name']}\n"
            f"Группа: {data['group_name']}\n"
            f"Стек: {data['stack']}"
        )
    else:
        await message.answer("Вы ещё не регистрировались. Отправьте /register для начала.")
