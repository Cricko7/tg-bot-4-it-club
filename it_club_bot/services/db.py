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

    async def delete_event(self, event_id: int):
        await self.conn.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
        await self.conn.execute("DELETE FROM event_participants WHERE event_id = ?", (event_id,))
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
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                registration_start DATE NOT NULL,
                registration_end DATE NOT NULL,
                event_start DATE NOT NULL,
                event_end DATE NOT NULL
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS event_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL
            )
        """)
        await self.conn.commit()
        print("Таблицы созданы или уже существуют")

    async def list_events(self):
        events = []
        async with self.conn.execute("SELECT event_id, title, event_start, event_end FROM events") as cursor:
            async for row in cursor:
                events.append({
                    "event_id": row[0],
                    "title": row[1],
                    "event_start": row[2],
                    "event_end": row[3],
                })
        return events

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

    async def add_event(self, title, description, reg_start, reg_end, ev_start, ev_end):
        await self.conn.execute(
            "INSERT INTO events (title, description, registration_start, registration_end, event_start, event_end) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, reg_start, reg_end, ev_start, ev_end)
        )
        await self.conn.commit()

    async def update_team_request_status(self, request_id: int, status: str):
        await self.conn.execute(
            "UPDATE team_requests SET status = ? WHERE id = ?",
            (status, request_id)
        )
        await self.conn.commit()

    async def get_user_events(self, user_id: int):
        events = []
        async with self.conn.execute("""
        SELECT e.event_id, e.title, e.event_start, e.event_end
        FROM events e
        JOIN event_participants p ON e.event_id = p.event_id
        WHERE p.user_id = ?
    """, (user_id,)) as cursor:
            async for row in cursor:
                events.append({
                "event_id": row[0],
                "title": row[1],
                "event_start": row[2],
                "event_end": row[3],
            })
        return events


    async def join_event(self, event_id: int, user_id: int) -> bool:
        async with self.conn.execute(
            "SELECT 1 FROM event_participants WHERE event_id = ? AND user_id = ?", (event_id, user_id)
        ) as cursor:
            if await cursor.fetchone():
                return False  # Уже записан
        await self.conn.execute(
            "INSERT INTO event_participants (event_id, user_id) VALUES (?, ?)", (event_id, user_id)
        )
        await self.conn.commit()
        return True

    async def get_event_participants(self, event_id: int):
        participants = []
        async with self.conn.execute(
            "SELECT user_id FROM event_participants WHERE event_id = ?", (event_id,)
        ) as cursor:
            async for row in cursor:
                participants.append(row[0])
        return participants

    async def get_event(self, event_id: int) -> Optional[dict]:
        async with self.conn.execute(
            "SELECT * FROM events WHERE event_id = ?", (event_id,)
        ) as cursor:
            row = await cursor.fetchone()
        if row:
            return {
                "event_id": row[0],
                "title": row[1],
                "description": row[2],
                "registration_start": row[3],
                "registration_end": row[4],
                "event_start": row[5],
                "event_end": row[6],
            }
        return None

