import asyncio
from aiogram import Bot, Dispatcher
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

db_instance = AsyncDB()

async def main():
    await db_instance.connect()
    await db_instance.init_db()

    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.middleware(DbMiddleware(db_instance))
    dp.callback_query.middleware(DbMiddleware(db_instance))
    dp.include_router(team_requests_router)
    dp.include_router(team_invitations_router)
    dp.include_router(admin_exports_router)  # router из вашего модуля с экспортом
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(teams.router)
    dp.include_router(admin.router)
    dp.include_router(admin_callbacks_router)
    dp.include_router(admin_panel_router)
    dp.include_router(user_commands.router)
    dp.include_router(events_router)
    dp.include_router(admin_remove_router)  # где admin_remove_router — импортированный router из файла с удалением


    await dp.start_polling(bot)
    await db_instance.close()
    await bot.session.close()
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
