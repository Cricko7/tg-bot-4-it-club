from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class DbMiddleware(BaseMiddleware):
    def __init__(self, db):
        super().__init__()
        self.db = db

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data["db"] = self.db
        return await handler(event, data)

