from datetime import date, datetime, timedelta, timezone, time
from html import escape
from aiogram import Bot

import logging

from ..db.users import get_user
from ..db.reminders import mark_reminder_sent, get_enabled_reminders
from ..db.blocked_lessons import get_blocked_lessons
from ..schedule.service import build_schedule_message, get_lessons_for_period, filter_blocked_lessons


logger = logging.getLogger(__name__)



async def build_reminder_message(
    reminder,
    target_date: date,
) -> str:
    action = reminder["action"]

    if action == "text":
        return escape(reminder["text"])

    if action == "schedule_today":
        schedule_date = target_date
        period = 1
    elif action == "schedule_tomorrow":
        schedule_date = target_date + timedelta(days=1)
        period = 1
    elif action == "schedule_week":
        schedule_date = target_date
        period = 7
    else:
        raise ValueError(f"Неизвестное действие напоминания: {action}")

    message = await build_schedule_message(reminder["telegram_id"], schedule_date, period)
    return message


async def get_reminder_datetime(
    reminder,
    target_date: date,
) -> datetime | None:
    user = await get_user(reminder["telegram_id"])
    if user is None:
        return None

    group_name, subgroup = user

    days = await get_lessons_for_period(group_name, subgroup, 1, target_date)
    if days is None:
        raise ValueError(f"Расписание не доступно: group={group_name}, date={target_date}")

    blocked_titles = set(
        await get_blocked_lessons(reminder["telegram_id"])
    )
    lessons = filter_blocked_lessons(days[0]["lessons"], blocked_titles)

    if not lessons:
        return None

    moscow_tz = timezone(timedelta(hours=3))

    if reminder["mode"] == "fixed":
        hours, minutes = divmod(reminder["time_minutes"], 60)
        return datetime.combine(
            target_date,
            time(hour=hours, minute=minutes),
            tzinfo=moscow_tz
        )
    elif reminder["mode"] == "before_first_lesson":
        start_times = []
        for lesson in lessons:
            start_text = lesson["time"].split("–", 1)[0].strip()
            start_time = datetime.strptime(start_text, "%H:%M").time()
            start_times.append(start_time)

        first_lesson = datetime.combine(
            target_date,
            min(start_times),
            tzinfo=moscow_tz,
        )
        return first_lesson - timedelta(
            minutes=reminder["offset_minutes"],
        )
    else:
        raise ValueError(f"Неизвестный режим: {reminder['mode']}")


async def check_reminders(bot: Bot):
    moscow_tz = timezone(timedelta(hours=3))
    reminders = await get_enabled_reminders()
    for reminder in reminders:
        try:
            now = datetime.now(moscow_tz)
            target_date = now.date()

            if reminder["last_sent_for_date"] == target_date.isoformat():
                continue

            reminder_datetime = await get_reminder_datetime(reminder, target_date)
            if reminder_datetime is None:
                continue

            now = datetime.now(moscow_tz)
            delay = now - reminder_datetime

            if timedelta(0) <= delay <= timedelta(minutes=1):
                message = await build_reminder_message(reminder, target_date)
                await bot.send_message(reminder["telegram_id"], message)
                await mark_reminder_sent(reminder["id"], target_date)

        except Exception:
            logger.exception(
                "Ошибка обработки напоминания id=%s, telegram_id=%s",
                reminder["id"],
                reminder["telegram_id"],
            )