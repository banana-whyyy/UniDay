from aiogram.types import Message

from ..db.users import get_user
from ..db.blocked_lessons import get_blocked_lessons
from ..keyboards.inline import blocked_lessons_keyboard, reminders_keyboard

from ..db.reminders import get_reminders


async def show_blocked_lessons(message: Message, telegram_id: int, edit: bool = False):
    user = await get_user(telegram_id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return

    lessons = await get_blocked_lessons(telegram_id)

    if not lessons:
        await message.answer(
            "🚫 Исключённые занятия\n\nПока ничего не исключено.",
            reply_markup=blocked_lessons_keyboard(),
        )
        return

    data = "🚫 Исключённые занятия\n\n" + "\n\n".join(
        f"• {lesson}" for lesson in lessons
    )
    send = message.edit_text if edit else message.answer
    await send(data, reply_markup=blocked_lessons_keyboard())


async def show_reminders(message: Message, telegram_id: int, edit: False):
    user = await get_user(telegram_id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return

    reminders = await get_reminders(telegram_id)

    if reminders == []:
        await message.answer("🔔 Напоминания\n\nНапоминаний пока нет.", reply_markup=reminders_keyboard())
        return


    action_titles = {
        "schedule_today": "Расписание на сегодня",
        "schedule_tomorrow": "Расписание на завтра",
        "schedule_week": "Расписание на неделю",
    }
    
    blocks = []
    for reminder in reminders:
        status = "✅" if reminder["is_enabled"] else "⏸"

        if reminder["mode"] == "fixed":
            hours, minutes = divmod(reminder["time_minutes"], 60)
            timing = f"В {hours:02d}:{minutes:02d} по Москве"
        else:
            timing = f"За {reminder['offset_minutes']} минут до первой пары"

        if reminder["action"] == "text":
            title = reminder["text"]
        else:
            title = action_titles[reminder["action"]]

        blocks.append(f"{status} {title}\n{timing}")

    data = "🔔 Напоминания:\n\n" + "\n\n".join(blocks)

    send = message.edit_text if edit else message.answer
    await send(data, reply_markup=reminders_keyboard())