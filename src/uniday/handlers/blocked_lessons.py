from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta, timezone
import httpx
import logging

from ..db.users import get_user
from ..db.blocked_lessons import get_blocked_lessons, add_blocked_lesson, remove_blocked_lesson

from ..schedule.service import get_lessons_for_period
from ..schedule.exceptions import ScheduleParseError
from ..keyboards.inline import blocked_lessons_keyboard, block_titles_keyboard
from .service import show_blocked_lessons


router = Router()

logger = logging.getLogger(__name__)



@router.message(Command("blocked"))
async def command_blocked(message: Message):
    await show_blocked_lessons(message, message.from_user.id)


@router.callback_query(F.data == "blocked")
async def show_blocked_callback(callback: CallbackQuery):
    await callback.answer()
    await show_blocked_lessons(callback.message, callback.from_user.id, edit=True)



@router.callback_query(F.data == "add_block")
async def add_block_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user = await get_user(callback.from_user.id)
    if user is None:
        await callback.message.answer("Сначала укажи группу и подгруппу через /start")
        return

    group_name, subgroup = user

    moscow_tz = timezone(timedelta(hours=3))
    moscow_now = datetime.now(moscow_tz)
    today = moscow_now.date()

    try:
        days = await get_lessons_for_period(group_name, subgroup, 14, today)
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: group=%s, date=%s, period=14",
            group_name,
            today,
        )
        await callback.message.answer("Не удалось загрузить расписание. Попробуй позже")
        return

    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: group=%s, date=%s, period=14",
            group_name,
            today,
        )
        await callback.message.answer("Не удалось обработать расписание. Попробуй позже")
        return

    if days is None:
        await callback.message.answer(
            "Не удалось получить расписание для выбора занятий"
        )
        return
    
    blocked = set(await get_blocked_lessons(callback.from_user.id))

    titles = set()
    for day in days:
        for lesson in day["lessons"]:
            if lesson["title"] not in blocked:
                titles.add(lesson["title"])

    if not titles:
        await callback.message.answer("Нет занятий для добавления")
        return 
    
    titles = sorted(titles)

    selection_message = await callback.message.answer(
        "Выбери занятие для исключения",
        reply_markup=block_titles_keyboard(titles, "add"),
    )
    await state.update_data(
        block_titles=titles,
        block_message_id=selection_message.message_id,
    )



@router.callback_query(F.data.startswith("block_add:"))
async def block_add_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    titles = data.get("block_titles")

    if titles is None:
        await callback.answer("Выбор устарел, открой /blocked заново")
        return

    if data.get("block_message_id") != callback.message.message_id:
        await callback.answer("Выбор устарел, открой /blocked заново")
        return

    try:
        index = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer("Некорректный выбор")
        return

    if not 0 <= index < len(titles):
        await callback.answer("Некорректный выбор")
        return

    await add_blocked_lesson(callback.from_user.id, titles[index])
    await state.update_data(block_titles=None, block_message_id=None)

    await callback.answer("Занятие добавлено")

    await callback.message.edit_text(
        f"Занятие добавлено в список исключений:\n\n{titles[index]}",
        reply_markup=blocked_lessons_keyboard(),
    )


@router.callback_query(F.data == "remove_block")
async def remove_block_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    blocked_lessons = await get_blocked_lessons(callback.from_user.id)
    if blocked_lessons == []:
        await callback.message.answer("Заблокированные занятия отсутствуют")
        return

    selection_message = await callback.message.answer(
        "Выбери занятие для удаления из списка",
        reply_markup=block_titles_keyboard(blocked_lessons, "remove"),
    )
    await state.update_data(
        block_titles=blocked_lessons,
        block_message_id=selection_message.message_id,
    )


@router.callback_query(F.data.startswith("block_remove:"))
async def block_remove_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    titles = data.get("block_titles")

    if titles is None:
        await callback.answer("Выбор устарел, открой /blocked заново")
        return

    if data.get("block_message_id") != callback.message.message_id:
        await callback.answer("Выбор устарел, открой /blocked заново")
        return

    try:
        index = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer("Некорректный выбор")
        return

    if not 0 <= index < len(titles):
        await callback.answer("Некорректный выбор")
        return

    await remove_blocked_lesson(callback.from_user.id, titles[index])
    await state.update_data(block_titles=None, block_message_id=None)

    await callback.answer("Занятие удалено из блока")

    await callback.message.edit_text(
        f"Занятие удалено из списка исключений:\n\n{titles[index]}",
        reply_markup=blocked_lessons_keyboard(),
    )