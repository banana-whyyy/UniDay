from bs4 import BeautifulSoup
from datetime import date


def parse_date(target_date: str) -> date:
    months = {
    "января": 1, "февраля": 2, "марта": 3,
    "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9,
    "октября": 10, "ноября": 11, "декабря": 12
    }

    day_text, months_text, year_text = target_date.split()
    return date(
        year=int(year_text),
        month=months[months_text],
        day=int(day_text)
    )



def parse_schedule(html: str):
    soup = BeautifulSoup(html, "html.parser")
    schedule = soup.select_one("div.table")

    if schedule is None:
        raise ValueError("В ответе нет таблицы расписания")

    days = []

    for day in schedule.find_all("div", recursive=False):
        date_text = day.find("strong").get_text(strip=True)
        current_time = None

        day_data = {
            "date": parse_date(date_text),
            "lessons": [],
        }

        for row in day.select("table tr"):
            cells = row.find_all("td", recursive=False)

            if len(cells) == 2:
                current_time = cells[0].get_text(strip=True)
                lesson_cell = cells[1]
            elif len(cells) == 1 and current_time is not None:
                lesson_cell = cells[0]
            else: 
                continue

            parts = [
                part.strip()
                for part in lesson_cell.get_text("|", strip=True).split("|")
                if part.strip()
            ]

            if len(parts) < 4:
                raise ValueError(f"Не удалось разобрать занятие: {parts}")

            subgroup = parts[1] if parts[1] in ("1 п.г.", "2 п.г.") else None
            if subgroup is not None:
                subgroup = int(subgroup.split()[0])

            # parts[2:-2] — пропускаем название и подгруппу, убираем аудиторию и преподавателя;
            # parts[1:-2] — пропускаем только название, потому что подгруппы нет.
            groups = parts[2:-2] if subgroup else parts[1:-2]


            lesson = {
                "time": current_time,
                "title": parts[0],
                "subgroup": subgroup,
                "groups": groups,
                "auditorium": parts[-2],
                "teacher": parts[-1]
            }
            day_data["lessons"].append(lesson)

        days.append(day_data)

    return days
