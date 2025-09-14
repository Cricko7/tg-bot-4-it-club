from aiogram.dispatcher.router import Router
from aiogram.filters import Command, Filter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

ADMIN_IDS = {1185406379, 780183740, 5612474540}  # Замените на свои ID админов

class AdminFilter(Filter):
    def __init__(self, admin_ids: set):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

admin_filter = AdminFilter(admin_ids=ADMIN_IDS)

def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stat")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="❌ Выйти из админки", callback_data="admin_exit")]
    ])
    return keyboard

@router.message(Command("adminpanel"), admin_filter)
async def admin_panel(message: Message):
    keyboard = get_admin_keyboard()
    await message.answer("Добро пожаловать в админ-панель.", reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("admin_"))
async def admin_callbacks(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    if callback.data == "admin_stat":
        await callback.message.edit_text("📊 Статистика бота:\nПользователей: 42\n... (пример)")
    elif callback.data == "admin_users":
        await callback.message.edit_text("👥 Список пользователей:\n1. User1\n2. User2\n3. User3\n...")
    elif callback.data == "admin_exit":
        await callback.message.edit_text("Вы вышли из админ-панели.")
    await callback.answer()
