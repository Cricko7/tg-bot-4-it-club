import io
import asyncio
import pandas as pd
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types.input_file import BufferedInputFile
from services.db import AsyncDB


router = Router()



ADMINS = {1185406379, 780183740, 5612474540}  # Сюда добавьте Telegram ID админов

@router.message(Command("export_users_csv"))
async def export_users_csv(message: types.Message, db: AsyncDB):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет прав для экспорта данных.")
        return

    # Получаем данные из базы, пример запроса (зависит от вашей БД/таблиц)
    users = []
    async with db.conn.execute("SELECT user_id, name, status FROM registrations") as cursor:
        async for row in cursor:
            users.append({
                "user_id": row[0],
                "name": row[1],
                "status": row[2],
            })

    if not users:
        await message.answer("Данных для экспорта нет.")
        return

    df = pd.DataFrame(users)
    buffer = io.StringIO()
    df.to_csv(buffer, sep=";", index=False)
    buffer.seek(0)
    csv_bytes = '\ufeff'.encode('utf-8') + buffer.getvalue().encode('utf-8')

    file = BufferedInputFile(csv_bytes, filename="users.csv")
    await message.answer_document(file)


@router.message(Command("export_teams_xlsx"))
async def export_teams_xlsx(message: types.Message, db: AsyncDB):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет прав для экспорта данных.")
        return

    teams = []
    query = """
        SELECT t.team_id, t.name, t.owner_id, r.name as owner_name
        FROM teams t
        LEFT JOIN registrations r ON t.owner_id = r.user_id
    """
    async with db.conn.execute(query) as cursor:
        async for row in cursor:
            teams.append({
                "team_id": row[0],
                "team_name": row[1],
                "owner_id": row[2],
                "owner_name": row[3] or "Неизвестно",
            })

    if not teams:
        await message.answer("Данных для экспорта нет.")
        return

    df = pd.DataFrame(teams)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Teams")
    buffer.seek(0)

    file = BufferedInputFile(buffer.read(), filename="teams.xlsx")
    await message.answer_document(file)