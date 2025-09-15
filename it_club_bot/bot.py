from config_ports import HTTP_PORT, HTTPS_PORT, BOT_POLLING_PORT, DATABASE_PORT
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from services.db import AsyncDB
from middlewares.db_middleware import DbMiddleware
from handlers import start, registration, teams, admin, user_commands
from handlers.team_requests import router as team_requests_router
from handlers.team_invitations import router as team_invitations_router
from handlers.admin_exports import router as admin_exports_router
from handlers.admin_remove import router as admin_remove_router
from handlers.admin_panel import router as admin_panel_router
from handlers.admin_callbacks import router as admin_callbacks_router
from handlers.events import router as events_router
from handlers.user_commands import router as user_commands_router
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # Преобразуем в список int

bot = Bot(token=TOKEN)
db_instance = AsyncDB()

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Старт бота"),
        BotCommand(command="register", description="Начать регистрацию"),
        BotCommand(command="mydata", description="Показать мои данные"),
        BotCommand(command="list_teams", description="Список команд"),
        BotCommand(command="list_events", description="Список мероприятий"),
        BotCommand(command="create_team", description="Создать команду"),
        BotCommand(command="join_team", description="Вступить в команду"),
        BotCommand(command="rename_team", description="Переименовать команду"),
        BotCommand(command="delete_team", description="Удалить команду"),
        BotCommand(command="my_events", description="Мои мероприятия"),
        BotCommand(command="join_event", description="Зарегистрироваться на мероприятие"),
        BotCommand(command="cancel_application", description="Отменить заявку"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="adminpanel", description="Панель администратора"),
        BotCommand(command="export_users_csv", description="Экспорт списка пользователей"),
        BotCommand(command="export_teams_xlsx", description="Экспорт списка команд"),
        BotCommand(command="export_event", description="Экспорт участников мероприятия"),
        BotCommand(command="remove_user", description="Удалить пользователя"),
        BotCommand(command="delete_event", description="Удалить мероприятие"),
        BotCommand(command="create_event", description="Создать мероприятие"),
        BotCommand(command="check_applications", description="Проверить заявки"),
        BotCommand(command="invite_requests", description="Просмотр заявок на приглашение"),
        BotCommand(command="manage_requests", description="Управление заявками"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await db_instance.connect()
    await db_instance.init_db()

    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DbMiddleware(db_instance))
    dp.callback_query.middleware(DbMiddleware(db_instance))

    # Регистрация всех роутеров
    dp.include_router(team_requests_router)
    dp.include_router(team_invitations_router)
    dp.include_router(admin_exports_router)
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(teams.router)
    dp.include_router(admin.router)
    dp.include_router(admin_callbacks_router)
    dp.include_router(admin_panel_router)
    dp.include_router(user_commands_router)
    dp.include_router(events_router)
    dp.include_router(admin_remove_router)
    # Назначаем команды Telegram
    await set_bot_commands(bot)

    await dp.start_polling(bot)

    await db_instance.close()
    await bot.session.close()
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    print("HTTP порт:", HTTP_PORT)
    print("HTTPS порт:", HTTPS_PORT)
    print("POLLING порт:", BOT_POLLING_PORT)
    print("DATABASE порт:", DATABASE_PORT)
    asyncio.run(main())
