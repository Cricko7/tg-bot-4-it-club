import sqlite3
import os
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DB_PATH = os.path.join(DATA_DIR, "itclub.db")

def init_db():
    print("Инициализация базы данных...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            group_name TEXT NOT NULL,
            stack TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Таблица registrations создана или уже существует")

def save_registration(user_id: int, name: str, group_name: str, stack: str):
    print(f"Сохраняем в базу: {user_id}, {name}, {group_name}, {stack}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO registrations (user_id, name, group_name, stack) VALUES (?, ?, ?, ?)",
            (user_id, name, group_name, stack)
        )
        conn.commit()
        print("Запись успешно сохранена")
    except Exception as e:
        print("Ошибка при сохранении в базу:", e)
    finally:
        conn.close()



def get_registration(user_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "user_id": row[1], "name": row[2],
            "group_name": row[3], "stack": row[4]
        }
    return None
