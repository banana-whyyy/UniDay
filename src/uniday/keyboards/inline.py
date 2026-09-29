from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def choose_subgroup_keyboard():
    buttons = [
        [InlineKeyboardButton(text="1-я подгруппа", callback_data="subgroup:1")],
        [InlineKeyboardButton(text="2-я подгруппа", callback_data="subgroup:2")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard