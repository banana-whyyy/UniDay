from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import re
from ..keyboards.inline import choose_subgroup_keyboard
from ..db.users import save_user, get_user



router = Router()


class Registration(StatesGroup):
    waiting_for_group = State()
    waiting_for_subgroup = State()



@router.message(Command("start"))
async def command_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user is None:
        await state.set_state(Registration.waiting_for_group)
        await message.answer("Привет! Напиши свою группу в виде\nИС2-251-ОБ")
    else:
        group_name, subgroup = user
        await message.answer(f"Твоя группа — {group_name}, подгруппа — {subgroup}")

@router.message(Registration.waiting_for_group)
async def receive_group(message: Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправьте название группы текстом")
        return
    
    if group_validator(message.text.strip().upper()):
        await state.update_data(group=message.text.strip().upper())
        await state.set_state(Registration.waiting_for_subgroup)
        await message.answer(
            "Выбери свою подгруппу",
            reply_markup=choose_subgroup_keyboard(),  
        )
    
    else:
        await message.answer("Пожалуйста, отправьте группу в нормальном виде")


@router.callback_query(
    Registration.waiting_for_subgroup,    
    F.data.in_({"subgroup:1", "subgroup:2"}),
)
async def receive_subgroup(callback: CallbackQuery, state: FSMContext):
    subgroup = int(callback.data.split(":")[1])
    data = await state.get_data()
    group = data["group"]

    await save_user(callback.from_user.id, group, subgroup)
    
    await callback.message.edit_text(f"Принял, группа {group}, подгруппа {subgroup}")
    await callback.answer()

    await state.clear()


def group_validator(group: str) -> bool:
    if re.fullmatch(r"[А-ЯЁ]+[124]-[0-9]{3,}-[А-ЯЁ]{2}", group):
        return True
    return False