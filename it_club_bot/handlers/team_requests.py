from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.db import AsyncDB

router = Router()

def get_request_kb(request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data=f"team_approve:{request_id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"team_reject:{request_id}"),
        ]
    ])

@router.message(Command("manage_requests"))
async def manage_requests(message: types.Message, db: AsyncDB):
    user_id = message.from_user.id
    team = await db.get_user_team(user_id)
    if not team:
        await message.answer("У вас нет команды.")
        return

    requests = await db.get_pending_team_requests(team['team_id'])

    if not requests:
        await message.answer("Нет новых заявок на вступление в вашу команду.")
        return

    for req in requests:
        kb = get_request_kb(req['id'])
        await message.answer(f"Заявка от {req['user_name']} (ID: {req['user_id']})", reply_markup=kb)

@router.callback_query(F.data.startswith("team_approve:"))
async def team_approve(call: CallbackQuery, db: AsyncDB):
    request_id = int(call.data.split(":")[1])
    await db.update_team_request_status(request_id, 'approved')
    await call.message.edit_text("Заявка одобрена.")
    await call.answer("Вы одобрили заявку.")

@router.callback_query(F.data.startswith("team_reject:"))
async def team_reject(call: CallbackQuery, db: AsyncDB):
    request_id = int(call.data.split(":")[1])
    await db.update_team_request_status(request_id, 'rejected')
    await call.message.edit_text("Заявка отклонена.")
    await call.answer("Вы отклонили заявку.")
