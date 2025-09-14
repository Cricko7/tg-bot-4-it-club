from aiogram import Router
from aiogram.types import CallbackQuery
from handlers.admin_utils import ADMIN_IDS

router = Router()

@router.callback_query(lambda c: c.data.startswith("admin_"))
async def admin_callbacks(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    if callback.data == "admin_stat":
        await callback.message.edit_text("📊 Статистика бота:\nПользователей: 42\n... (пример)")
    elif callback.data == "admin_users":
        await callback.message.edit_text("👥 Список пользователей:\n1. User1\n2. User2\n3. User3\n...")
    elif callback.data == "admin_exit":
        await callback.message.edit_text("Вы вышли из админ-панели.")
    await callback.answer()
