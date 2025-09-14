from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_IDS = {1185406379, 780183740, 5612474540}

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stat")],
        [InlineKeyboardButton(text="Заявки", callback_data="admin_users")],
        [InlineKeyboardButton(text="Выход", callback_data="admin_exit")]
    ])
