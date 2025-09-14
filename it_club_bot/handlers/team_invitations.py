from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.db import AsyncDB

router = Router()

def get_invite_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Отправить приглашение", callback_data=f"send_invite:{user_id}")
        ]
    ])

@router.message(Command("invite_requests"))
async def invite_requests(message: types.Message, db: AsyncDB):
    owner_id = message.from_user.id
    team = await db.get_user_team(owner_id)
    if not team:
        await message.answer("У вас нет команды.")
        return

    # Получаем заявки pending, которые подали пользователи, чтобы отправить им приглашение
    async with db.conn.execute(
        "SELECT id, user_id, user_name FROM team_requests WHERE team_id = ? AND status = 'pending'",
        (team['team_id'],)
    ) as cursor:
        requests = await cursor.fetchall()

    if not requests:
        await message.answer("Нет заявок для приглашения.")
        return

    for req_id, user_id, user_name in requests:
        kb = get_invite_kb(user_id)
        await message.answer(f"Заявка от {user_name} (ID: {user_id})", reply_markup=kb)

@router.callback_query(F.data.startswith("send_invite:"))
async def send_invite_callback(call: CallbackQuery, bot: Bot, db: AsyncDB):
    inviter_id = call.from_user.id
    user_id = int(call.data.split(":")[1])

    team = await db.get_user_team(inviter_id)
    if not team:
        await call.answer("У вас нет команды.", show_alert=True)
        return

    try:
        # Получаем приглашение на вступление (бот должен быть администратором группы)
        invite_link_obj = await bot.export_chat_invite_link(chat_id=team['team_id'])
        invite_link = invite_link_obj.invite_link

        # Отправляем приглашение пользователю
        await bot.send_message(user_id, f"Вас приглашают вступить в команду '{team['name']}'. Вот ссылка: {invite_link}")

        await call.answer("Приглашение отправлено.")
        await call.message.edit_text("Приглашение отправлено участнику.")
    except Exception as e:
        await call.answer(f"Ошибка отправки приглашения: {e}", show_alert=True)
