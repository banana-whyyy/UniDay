from aiogram import Bot
import logging
import asyncio

from .service import check_reminders


logger = logging.getLogger(__name__)


async def run_reminder_loop(bot: Bot):
    while True:
        try:
            await check_reminders(bot)
        except Exception:
            logger.exception(
                "Ошибка фоновой проверки напоминаний" 
            )
        # Тут пауза чтобы при сбое не случился непрерывный цикл
        await asyncio.sleep(30)