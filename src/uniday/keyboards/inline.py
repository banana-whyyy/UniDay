from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choose_subgroup_keyboard():
    buttons = [
        [InlineKeyboardButton(text="1-я подгруппа", callback_data="subgroup:1")],
        [InlineKeyboardButton(text="2-я подгруппа", callback_data="subgroup:2")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def blocked_lessons_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Добавить занятие", callback_data="add_block")],
        [InlineKeyboardButton(text="Удалить из списка", callback_data="remove_block")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# Решил переиспользовать клаву для block_add: и block_remove: 
def block_titles_keyboard(titles: list[str], action: str):
    buttons = []
    for index, title in enumerate(titles):
        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"block_{action}:{index}",
            )
        ])
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def reminders_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Добавить напоминание", callback_data="add_reminder")],
        [InlineKeyboardButton(text="Удалить напоминание", callback_data="remove_reminder")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def reminder_action_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Свой текст", callback_data="reminder_action:text")],
        [InlineKeyboardButton(text="Расписание на сегодня", callback_data="reminder_action:schedule_today")],
        [InlineKeyboardButton(text="Расписание на завтра", callback_data="reminder_action:schedule_tomorrow")],
        [InlineKeyboardButton(text="Расписание на неделю", callback_data="reminder_action:schedule_week")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def reminder_mode_keyboard():
    buttons = [
        [InlineKeyboardButton(text="В указанное время", callback_data="reminder_mode:fixed")],
        [InlineKeyboardButton(text="До первой пары", callback_data="reminder_mode:before_first_lesson")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def reminder_delete_keyboard(reminders):
    action_titles = {
        "schedule_today": "Расписание на сегодня",
        "schedule_tomorrow": "Расписание на завтра",
        "schedule_week": "Расписание на неделю",
    }
    buttons = []
    for reminder in reminders:
        if reminder["action"] == "text":
            title = reminder["text"]
        else:
            title = action_titles[reminder["action"]]

        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"reminder_delete:{reminder['id']}",
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def profile_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Изменить группу и подгруппу", callback_data="edit_profile")],
        [InlineKeyboardButton(text="Назад", callback_data="menu")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def cancel_inline_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_reminder")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard