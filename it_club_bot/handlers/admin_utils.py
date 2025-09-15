from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Преобразуем в список int


def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stat")],
        [InlineKeyboardButton(text="Заявки", callback_data="admin_users")],
        [InlineKeyboardButton(text="Выход", callback_data="admin_exit")]
    ])
