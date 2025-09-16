from aiogram.dispatcher.router import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, Filter
from aiogram.types import Message
from aiogram import types
from handlers.admin import get_admin_keyboard, ADMIN_IDS
from handlers.main_keyboard import get_main_keyboard
from services.db import AsyncDB
from aiogram.types import BotCommand
from aiogram import Bot
import os
from dotenv import load_dotenv

ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Преобразуем в список int
router = Router()
#admin_filter = AdminFilter(admin_ids=ADMIN_IDS)
load_dotenv()
# Создаём клавиатуру с командами
commands_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/create_team"), KeyboardButton(text="/join_team")],
        [KeyboardButton(text="/rename_team"), KeyboardButton(text="/delete_team")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def set_user_commands(bot: Bot):
    commands = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="help", description="Помощь и инструкции"),
    BotCommand(command="register", description="Начать регистрацию участника в системе"),
    BotCommand(command="mydata", description="Показать мои данные"),
    BotCommand(command="list_teams", description="Список команд (например, для вступления..)"),
    BotCommand(command="list_events", description="Просмотр мероприятий (для участия)"),
    BotCommand(command="create_team", description="Создать команду"),
    BotCommand(command="join_team", description="Вступить в команду"),
    BotCommand(command="rename_team", description="Переименовать команду"),
    BotCommand(command="delete_team", description="Удалить команду"),
    BotCommand(command="my_events", description="Мои мероприятия"),
    BotCommand(command="join_event", description="Записаться на мероприятие"),
    BotCommand(command="cancel_application", description="Отменить заявку (отказ от участия)"),
    # Команды, помеченные как админские, необязательно показывать всем
    BotCommand(command="adminpanel", description="Панель администратора"),
    BotCommand(command="export_users_csv", description="Экспорт списка пользователей"),
    BotCommand(command="export_teams_xlsx", description="Экспорт списка команд"),
    BotCommand(command="export_event", description="Экспорт участников мероприятия"),
    BotCommand(command="remove_user", description="Удалить пользователя"),
    BotCommand(command="delete_event", description="Удалить мероприятие"),
    BotCommand(command="create_event", description="Создать мероприятие"),
    BotCommand(command="check_applications", description="Проверить заявки (на вступление в клуб !)"),
    BotCommand(command="invite_requests", description="Просмотр заявок на приглашение (когда создатель команды приглашает кого-то в команду)"),
    BotCommand(command="manage_requests", description="Управление заявками (новых участников в команду)"),
    ]
    await bot.set_my_commands(commands)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Информация по функциям --> /help\nДля регистрации используй /register.\nВыберите кнопку:",
        reply_markup=keyboard
    )

# Остальные команды ...

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/register — начать регистрацию\n"
        "/mydata — показать ваши зарегистрированные данные\n"
        "\n После регистрации доступны след. команды:\n\n"
        "/create_team — создать команду \n"
        "/rename_team — переименовать команду \n"
        "/join_team — присоединиться к существующей команде \n"
        "/users_without_team — просмотреть список участников без команды \n"
        "/team_members — Вывести список участников в своей команде \n"
        ""
        ""
        ""
        ""
        ""
        ""
        ""
        ""
        ""
        ""
        ""
    )
    await message.answer(help_text)

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

@router.message(Command("cancel_application"))
async def cancel_application(message: types.Message, db: AsyncDB):
    user_id = message.from_user.id
    async with db.conn.execute("SELECT status FROM registrations WHERE user_id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
    if not row:
        await message.answer("У вас нет активной заявки.")
        return
    status = row[0]
    if status == "approved":
        await message.answer("Ваша заявка уже одобрена, отмена невозможна.")
        return
    if status == "cancelled":
        await message.answer("Вы уже отменяли заявку.")
        return
    await db.conn.execute("UPDATE registrations SET status = 'cancelled' WHERE user_id = ?", (user_id,))
    await db.conn.commit()
    await message.answer("Ваша заявка отменена. Вы можете подать новую заявку позже.")

@router.message(Command("team_members"))
async def team_members_handler(message: types.Message, db: AsyncDB):
    user_id = message.from_user.id
    # Получаем команду пользователя
    team = await db.get_user_team(user_id)
    if not team:
        await message.answer("Вы не состоите в команде.")
        return
    
    team_id = team['team_id']
    
    # Получаем список участников команды
    query = """
        SELECT r.user_id, r.name
        FROM registrations r
        JOIN teams_members tm ON r.user_id = tm.user_id
        WHERE tm.team_id = ?
    """
    members = []
    async with db.conn.execute(query, (team_id,)) as cursor:
        async for row in cursor:
            members.append(f"{row[1]} (ID: {row[0]})")
    
    if not members:
        await message.answer("В вашей команде пока нет участников.")
        return
    
    text = f"Участники команды '{team['name']}':\n\n" + "\n".join(members)
    await message.answer(text)

@router.message(Command("users_without_team"))
async def users_without_team_handler(message: types.Message, db: AsyncDB):
    query = """
        SELECT r.user_id, r.name
        FROM registrations r
        LEFT JOIN teams_members tm ON r.user_id = tm.user_id
        WHERE tm.user_id IS NULL
    """
    users = []
    async with db.conn.execute(query) as cursor:
        async for row in cursor:
            users.append(f"{row[1]} (ID: {row[0]})")

    if not users:
        await message.answer("Все пользователи уже состоят в командах.")
        return

    text = "Пользователи без команды:\n\n" + "\n".join(users)
    await message.answer(text)

@router.message(Command("mydata"))
async def cmd_mydata(message: types.Message, db: AsyncDB):
    user_id = message.from_user.id
    data = await db.get_registration(user_id)
    team = await db.get_user_team(user_id)

    if not data:
        await message.answer("Вы ещё не зарегистрированы.")
        return

    text = (
        f"Ваши данные:\n"
        f"ФИО: {data['name']}\n"
        f"Группа: {data['group_name']}\n"
        f"Стек: {data['stack']}\n"
    )
    if team:
        text += f"Вы состоите в команде: {team['name']}"
    else:
        text += "Вы не состоите ни в одной команде."

    await message.answer(text)
