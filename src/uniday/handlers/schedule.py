from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from datetime import datetime, timezone, timedelta
from ..db.users import get_user

from ..schedule.client import fetch_schedule_html
from ..schedule.parser import parse_schedule
from ..schedule.service import choose_day_and_lessons


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

    html = await fetch_schedule_html(group_name, today)

    days = parse_schedule(html)
    lessons = choose_day_and_lessons(days, today, group_name, subgroup)

    if lessons is None:
        await message.answer("Расписание на сегодня получить не удалось")
        return

    if lessons == []:
        await message.answer("На сегодня пар нет")
        return

    lines = []
    for lesson in lessons:
        lines.append(
            f"{lesson["time"]} - {lesson["title"]}\n"
            f"ауд. {lesson["auditorium"]}, {lesson["teacher"]}"
        )

    await message.answer("\n\n".join(lines))