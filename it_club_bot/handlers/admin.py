from aiogram import Router, types, Bot, F
from aiogram.filters import Command, Filter
from handlers.admin_utils import get_admin_keyboard, ADMIN_IDS
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.db import AsyncDB
from aiogram.types import Message
import os
from dotenv import load_dotenv

router = Router()

# Админские ID — замените на свои
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Преобразуем в список int


# Фильтр для админов
class AdminFilter(Filter):
    def __init__(self, admin_ids: set):
        self.admin_ids = admin_ids

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in self.admin_ids

admin_filter = AdminFilter(admin_ids=ADMIN_IDS)

admin_router = Router()

@admin_router.message(Command("help_adm"), admin_filter)
async def help_admin(message: Message):
    help_text = (
        "🛠 Команды администратора:\n\n"
        "/adminpanel - Открыть админ-панель\n"
        "/export_users_csv - Экспорт пользователей в CSV\n"
        "/export_teams_xlsx - Экспорт команд в XLSX\n"
        "/remove_user <id> - Удалить пользователя\n"
        "/delete_event <id> - Удалить мероприятие\n"
        "/create_event - Создать новое мероприятие\n"
        "/check_applications - Проверить заявки\n"
        "/invite_requests - Просмотр заявок на приглашение\n"
        "/manage_requests - Управление заявками\n"
        "/help_adm - Этот список команд\n"
    )
    await message.answer(help_text)

# Клавиатура админ-панели
@router.message(Command("adminpanel"), admin_filter)
async def admin_panel(message: types.Message, db: AsyncDB):
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

    stat_text = (
        f"📊 Статистика админ-панели:\n\n"
        f"👤 Зарегистрировано пользователей: {total_users}\n"
        f"👥 Количество команд: {total_teams}\n"
        f"🚫 Пользователей без команды: {users_without_team}"
    )
    await message.answer(stat_text)


@router.callback_query(F.data.startswith("admin_"))
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

# INLINE КЛАВИАТУРА ДЛЯ ЗАЯВОК
def get_application_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data=f"approve:{user_id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"reject:{user_id}"),
            InlineKeyboardButton(text="Подробнее", callback_data=f"details:{user_id}")
        ]
    ])

@router.message(Command("check_applications"), admin_filter)
async def check_applications(message: types.Message, db: AsyncDB):
    async with db.conn.execute("SELECT user_id, name FROM registrations WHERE status='pending'") as cursor:
        rows = await cursor.fetchall()
    if not rows:
        await message.answer("Нет новых заявок.")
        return
    for user_id, name in rows:
        kb = get_application_kb(user_id)
        await message.answer(f"Заявка от {name} (ID: {user_id})", reply_markup=kb)

@router.callback_query(F.data.startswith("approve:"), admin_filter)
async def approve_request(call: CallbackQuery, db: AsyncDB, bot: Bot):
    user_id = int(call.data.split(":")[1])
    await db.conn.execute("UPDATE registrations SET status = 'approved' WHERE user_id = ?", (user_id,))
    await db.conn.commit()

    group_link = "https://t.me/c/3018144642/1"  # замените на реальную ссылку

    await bot.send_message(user_id, f"Ваша заявка принята! Присоединяйтесь к группе: {group_link}")
    await call.message.edit_text(f"Заявка от пользователя ID {user_id} принята.")
    await call.answer("Заявка одобрена")

@router.callback_query(F.data.startswith("reject:"), admin_filter)
async def reject_request(call: CallbackQuery, db: AsyncDB):
    user_id = int(call.data.split(":")[1])
    await db.conn.execute("UPDATE registrations SET status = 'rejected' WHERE user_id = ?", (user_id,))
    await db.conn.commit()

    await call.message.edit_text(f"Заявка от пользователя ID {user_id} отклонена.")
    await call.answer("Заявка отклонена")

@router.callback_query(F.data.startswith("details:"), admin_filter)
async def show_application_details(callback: CallbackQuery, db: AsyncDB):
    user_id = int(callback.data.split(":")[1])
    async with db.conn.execute("SELECT user_id, name, group_name, stack, status FROM registrations WHERE user_id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
    if not row:
        await callback.message.answer(f"Заявка с user_id={user_id} не найдена.")
        return
    user_id, name, group_name, stack, status = row
    text = (
        f"Подробности заявки:\n"
        f"ID: {user_id}\n"
        f"ФИО: {name}\n"
        f"Группа: {group_name}\n"
        f"Стек: {stack}\n"
        f"Статус: {status}"
    )
    await callback.message.answer(text)
    await callback.answer()
