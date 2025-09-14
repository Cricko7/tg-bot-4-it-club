import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from services.db import AsyncDB
from middlewares.db_middleware import DbMiddleware
from handlers import start, registration, teams, admin, user_commands

db_instance = AsyncDB()

async def main():
    await db_instance.connect()
    await db_instance.init_db()

    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DbMiddleware(db_instance))
    dp.callback_query.middleware(DbMiddleware(db_instance))

    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(teams.router)
    dp.include_router(admin.router)
    dp.include_router(user_commands.router)

    await dp.start_polling(bot)
    await db_instance.close()
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
