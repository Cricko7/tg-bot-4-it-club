from aiogram import Router, types
from aiogram.filters import Command
from services.db import AsyncDB
from handlers.admin_utils import ADMIN_IDS, get_admin_keyboard

router = Router()

@router.message(Command("adminpanel"))
async def admin_panel(message: types.Message, db: AsyncDB):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет доступа к админ-панели.")
        return

    async with db.conn.execute("SELECT COUNT(*) FROM registrations") as cursor:
        total_users = (await cursor.fetchone())[0]

    async with db.conn.execute("SELECT COUNT(*) FROM teams") as cursor:
        total_teams = (await cursor.fetchone())[0]

    query = """
        SELECT COUNT(*) FROM registrations r
        LEFT JOIN teams_members tm ON r.user_id = tm.user_id
        WHERE tm.user_id IS NULL
    """
    async with db.conn.execute(query) as cursor:
        users_without_team = (await cursor.fetchone())[0]

    text = (
        f"📊 Статистика бота:\n\n"
        f"👤 Зарегистрировано пользователей: {total_users}\n"
        f"👥 Количество команд: {total_teams}\n"
        f"🚫 Пользователей без команды: {users_without_team}"
    )
    kb = get_admin_keyboard()
    await message.answer(text, reply_markup=kb)
