import aiosqlite
from ..config import settings

db_path = settings.database_path


async def add_blocked_lesson(telegram_id: int, lesson_title: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            INSERT INTO blocked_lessons(telegram_id, lesson_title)
            VALUES (?, ?)
            ON CONFLICT(telegram_id, lesson_title) DO NOTHING
        """, (telegram_id, lesson_title))

        await db.commit()


async def get_blocked_lessons(telegram_id: int) -> list[str]:
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("""
            SELECT lesson_title
            FROM blocked_lessons WHERE telegram_id = ?
        """, (telegram_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def remove_blocked_lesson(telegram_id: int, lesson_title: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            DELETE FROM blocked_lessons 
            WHERE telegram_id = ? AND lesson_title = ? 
        """, (telegram_id, lesson_title))

        await db.commit()