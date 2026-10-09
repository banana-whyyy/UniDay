from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from ..db.users import get_user
from ..keyboards.inline import profile_keyboard
from ..keyboards.main import menu_keyboard


router = Router()


@router.callback_query(F.data == "profile")
async def show_profile_callback(callback: CallbackQuery):
    await callback.answer()

    user = await get_user(callback.from_user.id)
    if user is None:
        await callback.message.answer("Пожалуйста зарегистрируйся по команде /start")
        return

    group, subgroup = user

    await callback.message.edit_text(f"👤 Профиль\n\nТвоя группа: {group}\nПодгруппа: {subgroup}", reply_markup=profile_keyboard())


@router.message(Command("menu"))
@router.message(F.text.in_({"Меню", "🧭 Меню"}))
async def menu_command(message: Message):
    await message.answer("🧭 Меню\nНастрой расписание и напоминания под себя.", reply_markup=menu_keyboard())


@router.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("🧭 Меню\n\nНастрой расписание и напоминания под себя.", reply_markup=menu_keyboard())