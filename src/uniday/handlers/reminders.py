from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..db.users import get_user
from ..db.reminders import get_reminders, add_reminder

from ..keyboards.inline import reminders_keyboard, reminder_mode_keyboard
from ..keyboards.reply import cancel_keyboard


router = Router()


@router.message(Command("reminders"))
async def command_reminders(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return

    reminders = await get_reminders(message.from_user.id)

    if reminders == []:
        await message.answer("Напоминаний пока нет", reply_markup=reminders_keyboard())
        return


    blocks = []
    for reminder in reminders:
        status = "✅" if reminder["is_enabled"] else "⏸"

        if reminder["mode"] == "fixed":
            hours, minutes = divmod(reminder["time_minutes"], 60)
            timing = f"В {hours:02d}:{minutes:02d} по Москве"
        else:
            timing = f"За {reminder['offset_minutes']} минут до первой пары"

        blocks.append(f"{status} {reminder['text']}\n{timing}")

    data = "Напоминания:\n\n" + "\n\n".join(blocks)

    await message.answer(data, reply_markup=reminders_keyboard())


class ReminderForm(StatesGroup):
    text = State()
    mode = State()
    time = State()


@router.callback_query(F.data == "add_reminder")
async def add_reminder_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user = await get_user(callback.from_user.id)
    if user is None:
        await callback.message.answer("Сначала укажи группу и подгруппу через /start")
        return

    await state.set_state(ReminderForm.text)
    await callback.message.answer("Введи текст напоминания", reply_markup=cancel_keyboard())


@router.message(ReminderForm(), F.text == "Отмена")
async def cancel_reminder(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание напоминания отменено", reply_markup=ReplyKeyboardRemove())


@router.message(ReminderForm.text, F.text)
async def receive_reminder(message: Message, state: FSMContext):
    if message.text.strip():
        await state.update_data(text=message.text.strip())
        await state.set_state(ReminderForm.mode)
        await message.answer("Когда напомнить?", reply_markup=reminder_mode_keyboard())

    else: 
        await message.answer("Текст напоминания не должен быть пустым")


@router.callback_query(
    ReminderForm.mode,
    F.data.in_({
        "reminder_mode:fixed",
        "reminder_mode:before_first_lesson",
    }),
)
async def receive_time_reminder(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    mode = callback.data.split(":", 1)[1]
    await state.update_data(mode=mode)

    await state.set_state(ReminderForm.time)
    await callback.message.edit_reply_markup(reply_markup=None)
    if mode == "fixed":
        await callback.message.answer("Введи время по Москве в формате ЧЧ:ММ\nНапример 12:20")
    
    else:
        await callback.message.answer("За сколько минут до первой пары напомнить?\nНапример, 90")


@router.message(ReminderForm.time, F.text)
async def create_reminder(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["mode"] == "fixed":
        try:
            hours_text, minutes_text = message.text.strip().split(":")
            hours, minutes = int(hours_text), int(minutes_text)
        except ValueError:
            await message.answer("Введи время в формате ЧЧ:ММ, например 12:20")
            return

        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            time_minutes = hours * 60 + minutes
            offset_minutes = None
        else:
            await message.answer("Часы < 24\nМинуты < 60")
            return

        
    else:
        try:
            offset_minutes = int(message.text.strip())
        except ValueError:
            await message.answer("Введи целое положительное число минут")
            return

        if offset_minutes <= 0:
            await message.answer("Количество минут должно быть больше нуля")
            return

        time_minutes = None
    
    await add_reminder(message.from_user.id, data["text"], data["mode"], time_minutes, offset_minutes)
    
    await state.clear()

    await message.answer(
        "Напоминание сохранено",
        reply_markup=ReplyKeyboardRemove(),
    )