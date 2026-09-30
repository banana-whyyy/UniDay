from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import httpx
import logging

from datetime import datetime, timezone, timedelta
from ..db.users import get_user

from ..schedule.service import get_lessons_for_date, format_lessons, get_lessons_for_period
from ..schedule.exceptions import ScheduleParseError


router = Router()

logger = logging.getLogger(__name__)


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


    try:
        lessons = await get_lessons_for_date(group_name, subgroup, today)
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: group=%s, date=%s",
            group_name,
            today,
        )
        await message.answer("Не удалось загрузить расписание. Попробуй позже")
        return

    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: group=%s, date=%s",
            group_name,
            today,
        )
        await message.answer("Не удалось обработать расписание. Попробуй позже")
        return


    if lessons is None:
        await message.answer("Расписание на сегодня получить не удалось")
        return

    if lessons == []:
        await message.answer("На сегодня пар нет")
        return

    await message.answer(format_lessons(lessons))


@router.message(Command("tomorrow"))
async def command_tomorrow(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return
    
    group_name, subgroup = user

    moscow_tz = timezone(timedelta(hours=3))
    moscow_now = datetime.now(moscow_tz)
    tomorrow = moscow_now.date() + timedelta(days=1)


    try:
        lessons = await get_lessons_for_date(group_name, subgroup, tomorrow)
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: group=%s, date=%s",
            group_name,
            tomorrow,
        )
        await message.answer("Не удалось загрузить расписание. Попробуй позже")
        return

    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: group=%s, date=%s",
            group_name,
            tomorrow,
        )
        await message.answer("Не удалось обработать расписание. Попробуй позже")
        return
    
    if lessons is None:
        await message.answer("Расписание на завтра получить не удалось")
        return

    if lessons == []:
        await message.answer("На завтра пар нет")
        return

    await message.answer(format_lessons(lessons))


@router.message(Command("week"))
async def command_week(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return

    group_name, subgroup = user

    moscow_tz = timezone(timedelta(hours=3))
    moscow_now = datetime.now(moscow_tz)
    today = moscow_now.date()


    try:
        days = await get_lessons_for_period(group_name, subgroup, 7, today)
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: group=%s, date=%s, period=7",
            group_name,
            today,
        )
        await message.answer("Не удалось загрузить расписание. Попробуй позже")
        return

    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: group=%s, date=%s, period=7",
            group_name,
            today,
        )
        await message.answer("Не удалось обработать расписание. Попробуй позже")
        return


    if days is None:
        await message.answer("Расписание на неделю получить не удалось")
        return

    weekdays = (
            "Понедельник", "Вторник", "Среда", "Четверг",
            "Пятница", "Суббота", "Воскресенье",
        )

    blocks = []
    for day in days:
        day_date = day["date"]
        lessons = day["lessons"]

        if lessons:
            schedule_text = format_lessons(lessons)
        else: 
            schedule_text = "Пар нет"

        day_name = weekdays[day_date.weekday()]
        blocks.append(f"{day_name}, {day_date:%d.%m.%Y}\n{schedule_text}")


    await message.answer("\n\n".join(blocks))