from aiogram import Router
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.db import AsyncDB
from aiogram.fsm.state import StatesGroup, State
import io
from aiogram.types import InputFile
from aiogram.types.input_file import BufferedInputFile
import csv
import pandas as pd

class EventStates(StatesGroup):
    title = State()
    description = State()
    reg_start = State()
    reg_end = State()
    event_start = State()
    event_end = State()

router = Router()

class AdminFilter(BaseFilter):
    def __init__(self, admin_ids: set):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

ADMIN_IDS = {1185406379, 780183740, 5612474540}
admin_filter = AdminFilter(admin_ids=ADMIN_IDS)

@router.message(Command("create_event"), admin_filter)
async def create_event_start(message: Message, state: FSMContext):
    await message.answer("Введите название мероприятия:")
    await state.set_state(EventStates.title)

@router.message(EventStates.title, admin_filter)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание мероприятия:")
    await state.set_state(EventStates.description)

@router.message(EventStates.description, admin_filter)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите дату начала регистрации (YYYY-MM-DD):")
    await state.set_state(EventStates.reg_start)

@router.message(EventStates.reg_start, admin_filter)
async def process_reg_start(message: Message, state: FSMContext):
    await state.update_data(reg_start=message.text)
    await message.answer("Введите дату окончания регистрации (YYYY-MM-DD):")
    await state.set_state(EventStates.reg_end)

@router.message(EventStates.reg_end, admin_filter)
async def process_reg_end(message: Message, state: FSMContext):
    await state.update_data(reg_end=message.text)
    await message.answer("Введите дату начала мероприятия (YYYY-MM-DD):")
    await state.set_state(EventStates.event_start)

@router.message(EventStates.event_start, admin_filter)
async def process_event_start(message: Message, state: FSMContext):
    await state.update_data(event_start=message.text)
    await message.answer("Введите дату окончания мероприятия (YYYY-MM-DD):")
    await state.set_state(EventStates.event_end)

@router.message(EventStates.event_end, admin_filter)
async def process_event_end(message: Message, state: FSMContext, db: AsyncDB):
    await state.update_data(event_end=message.text)
    data = await state.get_data()
    await db.add_event(
        title=data["title"],
        description=data["description"],
        reg_start=data["reg_start"],
        reg_end=data["reg_end"],
        ev_start=data["event_start"],
        ev_end=data["event_end"]
    )
    await message.answer("Мероприятие успешно добавлено!")
    await state.clear()

@router.message(Command("list_events"))
async def list_events_handler(message: Message, db: AsyncDB):
    events = await db.list_events()
    if not events:
        await message.answer("Мероприятий нет.")
        return
    text = "Список мероприятий:\n\n"
    for ev in events:
        text += f"[ID]\n {ev['event_id']}\n [Название] {ev['title']}\n\n [Период участия]: НАЧАЛО-КОНЕЦ (год-месяц-день):\n {ev['event_start']}–{ev['event_end']}\n"
    await message.answer(text)

@router.message(Command("event_details"))
async def event_details_handler(message: Message, db: AsyncDB):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Использование: /event_details <ID>")
        return
    event_id = int(args[1])
    event = await db.get_event(event_id)
    if not event:
        await message.answer("Мероприятие не найдено.")
        return
    text = (
        f"Название:\n {event['title']}\n\n"
        f"Описание:\n {event['description']}\n\n"
        f"\n Регистрация [НАЧАЛО-КОНЕЦ] (год-месяц-день):\n {event['registration_start']} — {event['registration_end']}\n"
        f"\n Мероприятие [НАЧАЛО-КОНЕЦ] (год-месяц-день):\n {event['event_start']} — {event['event_end']}"
    )
    await message.answer(text)

@router.message(Command("delete_event"), admin_filter)
async def delete_event_handler(message: Message, db: AsyncDB):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Использование: /delete_event <ID>")
        return
    event_id = int(args[1])
    await db.delete_event(event_id)
    await message.answer("Мероприятие удалено.")

@router.message(Command("join_event"))
async def join_event_handler(message: Message, db: AsyncDB):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Использование: /join_event <ID>")
        return
    event_id = int(args[1])
    user_id = message.from_user.id
    joined = await db.join_event(event_id, user_id)
    if not joined:
        await message.answer("Вы уже зарегистрированы на мероприятие.")
        return
    await message.answer("Вы успешно зарегистрировались на мероприятие.")

@router.message(Command("my_events"))
async def my_events_handler(message: Message, db: AsyncDB):
    user_id = message.from_user.id
    events = await db.get_user_events(user_id)
    if not events:
        await message.answer("Вы не зарегистрированы ни на одно мероприятие.")
        return
    text = "Ваши мероприятия:\n\n"
    for ev in events:
        text += f"[ID]\n {ev['event_id']}\n [Название] {ev['title']}\n [Даты] НАЧАЛО-КОНЕЦ (год-месяц-день):\n{ev['event_start']}–{ev['event_end']}\n"
    await message.answer(text)

@router.message(Command("export_event"), admin_filter)
async def export_event_handler(message: Message, db: AsyncDB):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Использование: /export_event <ID>")
        return

    event_id = int(args[1])

    query = """
        SELECT p.user_id, r.name, t.name as team_name, e.event_id, e.title, e.event_start
        FROM event_participants p
        JOIN registrations r ON p.user_id = r.user_id
        LEFT JOIN teams_members tm ON p.user_id = tm.user_id
        LEFT JOIN teams t ON tm.team_id = t.team_id
        JOIN events e ON p.event_id = e.event_id
        WHERE e.event_id = ?
    """

    participants = []
    async with db.conn.execute(query, (event_id,)) as cursor:
        async for row in cursor:
            participants.append({
                "User ID": row[0],
                "Name": row[1],
                "Team": row[2] or "Без команды",
                "Event ID": row[3],
                "Event Title": row[4],
                "Event Date": row[5]
            })

    if not participants:
        await message.answer("Участников нет.")
        return

    df = pd.DataFrame(participants)

    buffer = io.StringIO()
    df.to_csv(buffer, sep=";", index=False)
    buffer.seek(0)

    # Добавляем BOM для корректного отображения UTF-8 в Excel
    csv_bytes = '\ufeff'.encode('utf-8') + buffer.getvalue().encode('utf-8')

    file = BufferedInputFile(csv_bytes, filename="participants.csv")

    await message.answer_document(file)