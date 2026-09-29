from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from datetime import datetime, timezone, timedelta
from ..db.users import get_user

from ..schedule.service import get_lessons_for_date, format_lessons


router = Router()


@router.message(Command("today"))
async def command_today(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return

    group_name, subgroup = user

    moscow_tz = timezone(timedelta(hours=3))
    moscow_now = datetime.now(moscow_tz)
    today = moscow_now.date()


    lessons = await get_lessons_for_date(group_name, subgroup, today)

    if lessons is None:
        await message.answer("Расписание на сегодня получить не удалось")
        return

    if lessons == []:
        await message.answer("На сегодня пар нет")
        return

    await message.answer(format_lessons(lessons))


@router.message(Command("tommorow"))
async def command_tommorow(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return
    
    group_name, subgroup = user

    moscow_tz = timezone(timedelta(hours=3))
    moscow_now = datetime.now(moscow_tz)
    tommorow = moscow_now.date() + timedelta(days=1)

    lessons = await get_lessons_for_date(group_name, subgroup, tommorow)
    
    if lessons is None:
        await message.answer("Расписание на сегодня получить не удалось")
        return

    if lessons == []:
        await message.answer("На сегодня пар нет")
        return

    await message.answer(format_lessons(lessons))