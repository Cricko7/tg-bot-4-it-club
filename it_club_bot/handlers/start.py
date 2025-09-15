from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.admin_utils import get_admin_keyboard, ADMIN_IDS
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import Message
import os
from dotenv import load_dotenv

load_dotenv()


router = Router()

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/help"), KeyboardButton(text="/manage_requests")],
            [KeyboardButton(text="/list_teams"), KeyboardButton(text="/list_events")],
            [KeyboardButton(text="/check_applications"), KeyboardButton(text="/invite_requests")],
            [KeyboardButton(text="/delete_event"), KeyboardButton(text="/create_event")],
            [KeyboardButton(text="/export_event"), KeyboardButton(text="/remove_user")],
            [KeyboardButton(text="/export_teams_xlsx"), KeyboardButton(text="/export_users_csv")],
            [KeyboardButton(text="/adminpanel")]  # Админская, убрать для обычных пользователей
        ],
        resize_keyboard=True
    )
    return keyboard


@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = get_main_keyboard()  # вызов функции, возвращающей клавиатуру
    await message.answer("Добро пожаловать!", reply_markup=keyboard)

