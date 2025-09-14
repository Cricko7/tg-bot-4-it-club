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
        self.conn = await aiosqlite.connect(self.db_path, timeout=30)
        await self.conn.execute("PRAGMA busy_timeout = 30000")
        await self.conn.commit()


    async def is_user_approved(self, user_id: int) -> bool:
        async with self.conn.execute("SELECT status FROM registrations WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None and row[0] == "approved"


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
                stack TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                owner_id INTEGER NOT NULL
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS teams_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS team_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                team_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        await self.conn.commit()
        print("Таблицы созданы или уже существуют")


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


    async def get_user_team(self, user_id: int) -> Optional[dict]:
        async with self.conn.execute("""
            SELECT t.team_id, t.name FROM teams t
            JOIN teams_members m ON t.team_id = m.team_id
            WHERE m.user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {'team_id': row[0], 'name': row[1]}
            return None


    async def get_team_by_name(self, name: str) -> Optional[dict]:
        async with self.conn.execute("SELECT team_id, name FROM teams WHERE name = ?", (name,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {'team_id': row[0], 'name': row[1]}
            return None


    async def create_team(self, owner_id: int, name: str):
        await self.conn.execute("INSERT INTO teams (name, owner_id) VALUES (?, ?)", (name, owner_id))
        cursor = await self.conn.execute("SELECT last_insert_rowid()")
        team_id = (await cursor.fetchone())[0]
        await self.conn.execute("INSERT INTO teams_members (team_id, user_id) VALUES (?, ?)", (team_id, owner_id))
        await self.conn.commit()


    async def add_user_to_team(self, user_id: int, team_id: int):
        await self.conn.execute("INSERT INTO teams_members (team_id, user_id) VALUES (?, ?)", (team_id, user_id))
        await self.conn.commit()


    async def delete_team(self, team_id: int):
        await self.conn.execute("DELETE FROM teams_members WHERE team_id = ?", (team_id,))
        await self.conn.execute("DELETE FROM teams WHERE team_id = ?", (team_id,))
        await self.conn.commit()


    async def rename_team(self, owner_id: int, new_name: str):
        await self.conn.execute("UPDATE teams SET name = ? WHERE owner_id = ?", (new_name, owner_id))
        await self.conn.commit()


    async def list_teams(self):
        teams = []
        async with self.conn.execute("SELECT team_id, name FROM teams") as cursor:
            async for row in cursor:
                teams.append({'team_id': row[0], 'name': row[1]})
        return teams


    # Методы для заявок на вступление в команду


    async def add_team_request(self, user_id: int, user_name: str, team_id: int):
        await self.conn.execute(
            "INSERT INTO team_requests (user_id, user_name, team_id) VALUES (?, ?, ?)",
            (user_id, user_name, team_id)
        )
        await self.conn.commit()


    async def get_pending_team_requests(self, team_id: int):
        requests = []
        async with self.conn.execute(
            "SELECT id, user_id, user_name FROM team_requests WHERE team_id = ? AND status = 'pending'",
            (team_id,)
        ) as cursor:
            async for row in cursor:
                requests.append({'id': row[0], 'user_id': row[1], 'user_name': row[2]})
        return requests


    async def update_team_request_status(self, request_id: int, status: str):
        await self.conn.execute(
            "UPDATE team_requests SET status = ? WHERE id = ?",
            (status, request_id)
        )
        await self.conn.commit()
