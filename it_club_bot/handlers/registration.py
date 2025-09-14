from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services import db

router = Router()

class RegisterStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_group = State()
    waiting_for_stack = State()

@router.message(Command("register"))
async def cmd_register_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше ФИО:")
    await state.set_state(RegisterStates.waiting_for_name)

@router.message(RegisterStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите вашу учебную группу:")
    await state.set_state(RegisterStates.waiting_for_group)

@router.message(RegisterStates.waiting_for_group)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer("Введите ваш стек технологий:")
    await state.set_state(RegisterStates.waiting_for_stack)

@router.message(RegisterStates.waiting_for_stack)
async def process_stack(message: types.Message, state: FSMContext):
    await state.update_data(stack=message.text)
    data = await state.get_data()
    user_id = message.from_user.id

    # Сохраняем в базу
    db.save_registration(
        user_id=user_id,
        name=data["name"],
        group_name=data["group"],
        stack=data["stack"]
    )

    await message.answer(
        f"Регистрация завершена!\n\n"
        f"ФИО: {data['name']}\n"
        f"Группа: {data['group']}\n"
        f"Стек: {data['stack']}\n\n"
        "Спасибо за вашу заявку!"
    )
    await state.clear()
