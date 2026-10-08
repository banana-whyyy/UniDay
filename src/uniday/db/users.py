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
        await db.execute("PRAGMA foreign_keys = ON")

        await db.execute("""
                CREATE TABLE IF NOT EXISTS blocked_lessons (
                    telegram_id INTEGER NOT NULL REFERENCES users(telegram_id),
                    lesson_title TEXT NOT NULL,
                    PRIMARY KEY (telegram_id, lesson_title)
                )
        """)

        await db.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY,
                    telegram_id INTEGER NOT NULL REFERENCES users(telegram_id),
                    text TEXT NOT NULL,
                    mode TEXT NOT NULL CHECK (
                        mode IN ('fixed', 'before_first_lesson')
                    ),
                    time_minutes INTEGER,
                    offset_minutes INTEGER,
                    is_enabled INTEGER NOT NULL DEFAULT 1 CHECK (
                        is_enabled IN (0, 1)
                    ),
                    last_sent_for_date TEXT,
                    action TEXT NOT NULL DEFAULT 'text' CHECK
                        (
                            action IN ('text', 'schedule_today', 'schedule_tomorrow', 'schedule_week')
                        ),
                    CHECK (
                        (
                            mode = 'fixed'
                            AND time_minutes IS NOT NULL
                            AND time_minutes BETWEEN 0 AND 1439
                            AND offset_minutes IS NULL
                        )
                        OR
                        (
                            mode = 'before_first_lesson'
                            AND offset_minutes IS NOT NULL
                            AND offset_minutes > 0
                            AND time_minutes IS NULL
                        )
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