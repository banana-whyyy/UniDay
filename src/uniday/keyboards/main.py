from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Исключенные занятия", callback_data="blocked")],
        [InlineKeyboardButton(text="Напоминания", callback_data="reminders")],
        [InlineKeyboardButton(text="Профиль", callback_data="profile")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
