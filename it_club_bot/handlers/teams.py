from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from services.db import AsyncDB


router = Router()


class TeamStates(StatesGroup):
    creating = State()
    renaming = State()
    joining = State()


@router.message(Command("create_team"))
async def create_team(message: types.Message, state: FSMContext, db: AsyncDB):
    user_id = message.from_user.id
    approved = await db.is_user_approved(user_id)
    if not approved:
        await message.answer("Ваша заявка ещё не одобрена или была отклонена. Вы не можете создавать или изменять команды.")
        return
    await message.answer("Введите название команды:")
    await state.set_state(TeamStates.creating)


@router.message(TeamStates.creating)
async def create_team_process(message: types.Message, state: FSMContext, db: AsyncDB):
    team_name = message.text.strip()
    user_id = message.from_user.id
    existing_team = await db.get_user_team(user_id)
    if existing_team:
        await message.answer(f"У вас уже есть команда: {existing_team['name']}. Сначала удалите или переименуйте её.")
        await state.clear()
        return
    await db.create_team(user_id, team_name)
    await message.answer(f"Команда '{team_name}' успешно создана!")
    await state.clear()


@router.message(Command("delete_team"))
async def delete_team(message: types.Message, db: AsyncDB):
    user_id = message.from_user.id
    approved = await db.is_user_approved(user_id)
    if not approved:
        await message.answer("Вы не можете удалять команды, так как ваша заявка не одобрена.")
        return
    team = await db.get_user_team(user_id)
    if not team:
        await message.answer("У вас нет команды для удаления.")
        return
    await db.delete_team(team['team_id'])
    await message.answer(f"Команда '{team['name']}' удалена.")


@router.message(Command("rename_team"))
async def rename_team_start(message: types.Message, state: FSMContext, db: AsyncDB):
    user_id = message.from_user.id
    approved = await db.is_user_approved(user_id)
    if not approved:
        await message.answer("Вы не можете переименовывать команды, так как ваша заявка не одобрена.")
        return
    team = await db.get_user_team(user_id)
    if not team:
        await message.answer("У вас нет команды для переименования.")
        return
    await message.answer("Введите новое название команды:")
    await state.set_state(TeamStates.renaming)


@router.message(TeamStates.renaming)
async def rename_team_process(message: types.Message, state: FSMContext, db: AsyncDB):
    new_name = message.text.strip()
    user_id = message.from_user.id
    await db.rename_team(user_id, new_name)
    await message.answer(f"Команда переименована в '{new_name}'")
    await state.clear()


@router.message(Command("join_team"))
async def join_team_start(message: types.Message, state: FSMContext, db: AsyncDB):
    user_id = message.from_user.id
    approved = await db.is_user_approved(user_id)
    if not approved:
        await message.answer("Вы не можете присоединяться к командам, так как ваша заявка не одобрена.")
        return
    await message.answer("Введите название команды, к которой хотите присоединиться:")
    await state.set_state(TeamStates.joining)


@router.message(TeamStates.joining)
async def join_team_process(message: types.Message, state: FSMContext, db: AsyncDB):
    team_name = message.text.strip()
    user_id = message.from_user.id
    team = await db.get_team_by_name(team_name)
    if not team:
        await message.answer(f"Команда '{team_name}' не найдена.")
        await state.clear()
        return
    await db.add_user_to_team(user_id, team['team_id'])
    await message.answer(f"Вы присоединились к команде '{team_name}'")
    await state.clear()


@router.message(Command("list_teams"))
async def list_teams_handler(message: types.Message, db: AsyncDB):
    teams = await db.list_teams()
    if not teams:
        await message.answer("Пока нет ни одной команды.")
        return
    text = "Список существующих команд:\n\n"
    text += "\n".join(f"- {team['name']} (ID: {team['team_id']})" for team in teams)
    await message.answer(text)
