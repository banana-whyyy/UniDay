from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Исключенные занятия", callback_data="blocked")],
        [InlineKeyboardButton(text="Напоминания", callback_data="reminders")],
        [InlineKeyboardButton(text="Профиль", callback_data="profile")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def main_keyboard():
    buttons = [
        [
            KeyboardButton(text="📅 Сегодня"),
            KeyboardButton(text="➡️ Завтра"),
            KeyboardButton(text="☀️ Неделя"),
        ],
        [KeyboardButton(text="🧭 Меню")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard 