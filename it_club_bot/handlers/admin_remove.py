from aiogram import Router, types
from aiogram.filters import Command
from services.db import AsyncDB
import os
from dotenv import load_dotenv

router = Router()

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Преобразуем в список int


@router.message(Command("remove_user"))
async def remove_user(message: types.Message, db: AsyncDB):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав для удаления участников.")
        return

    args = message.text.strip().split()
    if len(args) < 2:
        await message.answer("Пожалуйста, укажите user_id для удаления.\nПример: /remove_user 123456")
        return

    user_id = args[1]

    await db.conn.execute("DELETE FROM registrations WHERE user_id = ?", (user_id,))
    await db.conn.commit()

    await message.answer(f"Пользователь с user_id={user_id} был удалён.")


@router.message(Command("remove_team"))
async def remove_team(message: types.Message, db: AsyncDB):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав для удаления команд.")
        return

    args = message.text.strip().split()
    if len(args) < 2:
        await message.answer("Пожалуйста, укажите team_id для удаления.\nПример: /remove_team 98765")
        return

    team_id = args[1]

    await db.conn.execute("DELETE FROM teams WHERE team_id = ?", (team_id,))
    await db.conn.commit()

    await message.answer(f"Команда с team_id={team_id} была удалена.")
