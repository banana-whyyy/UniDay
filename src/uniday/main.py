from aiogram import Bot, Dispatcher
import asyncio
import logging
import sys
from contextlib import suppress

from .reminders.scheduler import run_reminder_loop
from .config import settings
from .handlers import menu, onboarding, schedule, blocked_lessons, reminders
from .db.users import init_db


logger = logging.getLogger(__name__)


async def main():
    logger.info("Инициализация базы данных...")
    await init_db()

    token = settings.bot_token


    dp = Dispatcher()
    bot = Bot(token=token)

    dp.include_router(onboarding.router)
    dp.include_router(schedule.router)
    dp.include_router(blocked_lessons.router)
    dp.include_router(reminders.router)
    dp.include_router(menu.router)

    reminder_task = asyncio.create_task(run_reminder_loop(bot))

    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot, close_bot_session=False)
    finally:
        reminder_task.cancel()
        with suppress(asyncio.CancelledError):
            await reminder_task
        await bot.session.close()


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout, 
        )
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")