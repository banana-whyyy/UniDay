from datetime import date



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

