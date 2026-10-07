import aiosqlite
from ..config import settings

db_path = settings.database_path


async def add_reminder(
    telegram_id: int,
    text: str,
    mode: str,
    time_minutes: int | None = None,
    offset_minutes: int | None = None
) -> int:
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        cursor = await db.execute("""
            INSERT INTO reminders(telegram_id, text, mode, time_minutes, offset_minutes)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, text, mode, time_minutes, offset_minutes))

        await db.commit()

        return cursor.lastrowid


async def get_reminders(telegram_id: int):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, text, action, mode, time_minutes, offset_minutes, is_enabled
            FROM reminders
            WHERE telegram_id = ?
            ORDER BY id
        """, (telegram_id,))

        rows = await cursor.fetchall()
        return rows


async def remove_reminder(telegram_id: int, reminder_id: int):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            DELETE FROM reminders
            WHERE id = ? AND telegram_id = ?
        """, (reminder_id, telegram_id))

        await db.commit()


async def set_reminder_enabled(
    telegram_id: int,
    reminder_id: int,
    is_enabled: bool,
):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            UPDATE reminders
            SET is_enabled = ? 
            WHERE id = ? AND telegram_id = ?
        """, (int(is_enabled), reminder_id, telegram_id))

        await db.commit()