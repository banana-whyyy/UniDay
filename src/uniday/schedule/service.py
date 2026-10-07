from datetime import date, timedelta
from html import escape

from ..db.users import get_user
from ..db.blocked_lessons import get_blocked_lessons

from .parser import parse_schedule
from .client import fetch_schedule_html



def choose_day_and_lessons(
    days: list[dict], 
    target_date: date, 
    group: str, 
    subgroup: int,
) -> list[dict] | None:
    for day in days:
        if day["date"] == target_date:
            selected_lessons = []

            for lesson in day["lessons"]:
                if group not in lesson["groups"]:
                    continue

                if lesson["subgroup"] is None or lesson["subgroup"] == subgroup:
                    selected_lessons.append(lesson)

            return selected_lessons

    return None


def format_lessons(lessons: list[dict]) -> str:
    lines = []
    for lesson in lessons:
        lines.append(
            f"{escape(lesson['time'])} — {escape(lesson['title'])}\n"
            f"ауд. {escape(lesson['auditorium'])}, {escape(lesson['teacher'])}"
        )
    return "\n\n".join(lines)


async def get_lessons_for_period(
    group: str, 
    subgroup: int, 
    period: int,
    target_date: date,
) -> list[dict] | None:
    html = await fetch_schedule_html(group, target_date)
    days = parse_schedule(html) 

    data = []
    for offset in range(period):
        current_date = target_date + timedelta(days=offset)
        lessons = choose_day_and_lessons(days, current_date, group, subgroup)
        if lessons is None:
            return None

        data.append({"date": current_date, "lessons": lessons})

    return data


def filter_blocked_lessons(
    lessons: list[dict],
    blocked_titles: set[str],
) -> list[dict]:
    result = []

    for lesson in lessons:
        if lesson["title"] in blocked_titles:
            continue
        result.append(lesson)
        
    return result


async def build_schedule_message(
    telegram_id: int,
    target_date: date,
    period: int = 1,
) -> str:
    user = await get_user(telegram_id)
    if user is None:
        return "Сначала укажи группу и подгруппу через /start"

    group_name, subgroup = user

    days = await get_lessons_for_period(group_name, subgroup, period, target_date)

    if days is None:
        return "Не удалось получить расписание"

    blocked_titles = set(await get_blocked_lessons(telegram_id))
    weekdays = (
        "Понедельник", "Вторник", "Среда", "Четверг",
        "Пятница", "Суббота", "Воскресенье",
    )

    blocks = []

    for day in days:
        day_date = day["date"]
        lessons = filter_blocked_lessons(day["lessons"], blocked_titles)

        if lessons:
            schedule_text = format_lessons(lessons)
        elif day["lessons"]:
            schedule_text = "Все занятия исключены"
        else: 
            schedule_text = "Пар нет"

        day_name = weekdays[day_date.weekday()]
        blocks.append(
            f"📅 <b>{day_name}, {day_date:%d.%m.%Y}</b>\n\n{schedule_text}"
        )

    return "\n\n".join(blocks)