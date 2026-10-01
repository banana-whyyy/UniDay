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