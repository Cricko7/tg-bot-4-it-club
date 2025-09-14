import aiosqlite
import os
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DB_PATH = os.path.join(DATA_DIR, "itclub.db")

class AsyncDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("PRAGMA busy_timeout = 30000")
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def init_db(self):
        print("Инициализация базы данных...")
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                stack TEXT NOT NULL
            )
        """)
        await self.conn.commit()
        print("Таблица registrations создана или уже существует")

    async def save_registration(self, user_id: int, name: str, group_name: str, stack: str):
        print(f"Сохраняем в базу: {user_id}, {name}, {group_name}, {stack}")
        try:
            await self.conn.execute(
                "INSERT INTO registrations (user_id, name, group_name, stack) VALUES (?, ?, ?, ?)",
                (user_id, name, group_name, stack)
            )
            await self.conn.commit()
            print("Запись успешно сохранена")
        except Exception as e:
            print(f"Ошибка при сохранении в базу: {e}")

    async def get_registration(self, user_id: int) -> Optional[dict]:
        async with self.conn.execute("SELECT * FROM registrations WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_id": row[1],
                    "name": row[2],
                    "group_name": row[3],
                    "stack": row[4],
                }
            return None
