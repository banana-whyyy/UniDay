from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command("start"))
async def command_start(message: Message):
    await message.answer("Привет! Напиши свою группу")