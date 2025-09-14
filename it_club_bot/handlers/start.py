from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.admin_utils import get_admin_keyboard, ADMIN_IDS


router = Router()


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/help"),KeyboardButton(text="/register")],
        [KeyboardButton(text="/list_teams"),KeyboardButton(text="/adminpanel")],
        [KeyboardButton(text="/create_team"), KeyboardButton(text="/join_team")],
        [KeyboardButton(text="/rename_team"), KeyboardButton(text="/delete_team")],
        [KeyboardButton(text="/rename_team"), KeyboardButton(text="/delete_team")],
        [KeyboardButton(text="/cancel_application"), KeyboardButton(text="/mydata")]
    ],
    resize_keyboard=True
)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Информация по функциям --> /help\nДля регистрации используй /register.\nВыберите кнопку:",
        reply_markup=keyboard
    )
