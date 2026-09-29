import aiosqlite
from ..config import settings

db_path = settings.database_path


async def init_db():
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    group_name TEXT NOT NULL,
                    subgroup INTEGER NOT NULL CHECK (
                        subgroup IN (1, 2)
                    )
                )
        """)

        await db.commit()


async def save_user(telegram_id: int, group_name: str, subgroup: int):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            INSERT INTO users (telegram_id, group_name, subgroup)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                group_name = excluded.group_name,
                subgroup = excluded.subgroup
        """, (telegram_id, group_name, subgroup))

        await db.commit()


async def get_user(telegram_id: int):
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("""
            SELECT group_name, subgroup
            FROM users WHERE telegram_id = ?
        """, (telegram_id,))

        row = await cursor.fetchone()
        return row