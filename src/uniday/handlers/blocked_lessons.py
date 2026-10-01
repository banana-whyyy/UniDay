from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..db.users import get_user
from ..db.blocked_lessons import get_blocked_lessons


router = Router()


@router.message(Command("blocked"))
async def command_blocked(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала укажи группу и подгруппу через /start")
        return

    lessons = await get_blocked_lessons(message.from_user.id)

    if lessons == []:
        await message.answer("Список исключенных пар пуст")
        return

    data = "Заблокированные пары:\n\n" + "\n\n".join(lessons)

    await message.answer(data)

    