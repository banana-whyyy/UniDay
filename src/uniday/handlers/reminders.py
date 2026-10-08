from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..db.users import get_user
from ..db.reminders import get_reminders, add_reminder, remove_reminder
from .service import show_reminders

from ..keyboards.inline import reminders_keyboard, reminder_mode_keyboard, reminder_delete_keyboard, reminder_action_keyboard
from ..keyboards.reply import cancel_keyboard


router = Router()


@router.message(Command("reminders"))
async def command_reminders(message: Message):
    await show_reminders(message, message.from_user.id)


@router.callback_query(F.data == "reminders")
async def show_reminders_callback(callback: CallbackQuery):
    await callback.answer()
    await show_reminders(callback.message, callback.from_user.id)


class ReminderForm(StatesGroup):
    action = State()
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

    await state.set_state(ReminderForm.action)
    await callback.message.answer("Выбери действие", reply_markup=reminder_action_keyboard())


@router.callback_query(ReminderForm.action, F.data.startswith("reminder_action:"))
async def choose_action_reminder(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":", 1)[1]

    if action not in {
        "text",
        "schedule_today",
        "schedule_tomorrow",
        "schedule_week",
    }:
        await callback.answer("Некорректное действие")
        return

    await callback.answer()
    await state.update_data(action=action)
    await callback.message.edit_reply_markup(reply_markup=None)

    if action == "text":
        await state.set_state(ReminderForm.text)
        await callback.message.answer("Введи текст напоминания", reply_markup=cancel_keyboard())
    else:
        await state.update_data(text="")
        await state.set_state(ReminderForm.mode)
        await callback.message.answer("Когда напомнить?", reply_markup=reminder_mode_keyboard())



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
        await callback.message.answer("Введи время по Москве в формате ЧЧ:ММ\nНапример 12:20", reply_markup=cancel_keyboard())
    
    else:
        await callback.message.answer("За сколько минут до первой пары напомнить?\nНапример, 90", reply_markup=cancel_keyboard())


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
    
    await add_reminder(
        telegram_id=message.from_user.id,
        text=data["text"],
        mode=data["mode"],
        action=data["action"],
        time_minutes=time_minutes,
        offset_minutes=offset_minutes,
    )
    
    await state.clear()

    await message.answer(
        "Напоминание сохранено",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.callback_query(F.data == "remove_reminder")
async def remove_reminder_button(callback: CallbackQuery):
    await callback.answer()

    reminders = await get_reminders(callback.from_user.id)
    if reminders == []:
        await callback.message.answer("Список напоминаний пуст")
        return

    await callback.message.answer(
        "Выбери напоминание для удаления",
        reply_markup=reminder_delete_keyboard(reminders),
    )


@router.callback_query(F.data.startswith("reminder_delete:"))
async def delete_reminder_handler(callback: CallbackQuery, state: FSMContext):
    try:
        reminder_id = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer("Некорректный выбор")
        return
    
    await remove_reminder(callback.from_user.id, reminder_id)
    await callback.answer("Напоминание удалено")
    await callback.message.edit_text(
        "Напоминание удалено",
        reply_markup=reminders_keyboard(),
    )