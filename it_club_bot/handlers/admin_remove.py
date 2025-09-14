from aiogram import Router, types
from aiogram.filters import Command
from services.db import AsyncDB

router = Router()

ADMINS = {1185406379, 780183740, 5612474540}  # Здесь укажите Telegram ID админов

@router.message(Command("remove_user"))
async def remove_user(message: types.Message, db: AsyncDB):
    if message.from_user.id not in ADMINS:
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
    if message.from_user.id not in ADMINS:
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
