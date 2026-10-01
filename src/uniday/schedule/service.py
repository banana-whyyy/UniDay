from datetime import date, timedelta
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



async def get_lessons_for_date(group: str, subgroup: int, target_date: date) -> list[dict] | None:
    html = await fetch_schedule_html(group, target_date)
    days = parse_schedule(html)   
    return choose_day_and_lessons(days, target_date, group, subgroup)


def format_lessons(lessons: list[dict]) -> str:
    lines = []
    for lesson in lessons:
        lines.append(
            f"{lesson["time"]} - {lesson["title"]}\n"
            f"ауд. {lesson["auditorium"]}, {lesson["teacher"]}"
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