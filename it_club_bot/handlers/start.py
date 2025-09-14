from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from handlers.admin import get_admin_keyboard, ADMIN_IDS
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "Добро пожаловать, админ! Вот ваша панель:",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer("Привет! Для регистрации используй /register.")
