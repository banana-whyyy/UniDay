from aiogram import Bot, Dispatcher
import asyncio

from .config import settings
from .handlers.onboarding import router as onboarding_router
from .handlers.schedule import router as schedule_router
from .db.users import init_db


async def main():
    await init_db()

    token = settings.bot_token


    dp = Dispatcher()
    bot = Bot(token=token)

    dp.include_router(onboarding_router)
    dp.include_router(schedule_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())