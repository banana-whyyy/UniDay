from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
    )