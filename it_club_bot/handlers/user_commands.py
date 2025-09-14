from aiogram.dispatcher.router import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import types
from handlers.admin import get_admin_keyboard, ADMIN_IDS
from handlers.main_keyboard import get_main_keyboard
from services.db import AsyncDB

router = Router()

# Создаём клавиатуру с командами
commands_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/create_team"), KeyboardButton(text="/join_team")],
        [KeyboardButton(text="/rename_team"), KeyboardButton(text="/delete_team")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


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
