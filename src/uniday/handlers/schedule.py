from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import httpx
import logging

from datetime import datetime, timezone, timedelta

from ..schedule.service import build_schedule_message
from ..schedule.exceptions import ScheduleParseError


router = Router()

logger = logging.getLogger(__name__)


@router.message(Command("today"))
@router.message(F.text.in_({"Сегодня", "📅 Сегодня"}))
async def command_today(message: Message):
    moscow_tz = timezone(timedelta(hours=3))
    today = datetime.now(moscow_tz).date()

    try:
        text = await build_schedule_message(
            telegram_id=message.from_user.id,
            target_date=today,
        )
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: telegram_id=%s, date=%s",
            message.from_user.id,
            today,
        )
        await message.answer("Не удалось загрузить расписание. Попробуй позже")
        return
    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: telegram_id=%s, date=%s",
            message.from_user.id,
            today,
        )
        await message.answer("Не удалось обработать расписание. Попробуй позже")
        return

    await message.answer(text, parse_mode="HTML")


@router.message(Command("tomorrow"))
@router.message(F.text.in_({"Завтра", "➡️ Завтра"}))
async def command_tomorrow(message: Message):
    moscow_tz = timezone(timedelta(hours=3))
    tomorrow = datetime.now(moscow_tz).date() + timedelta(days=1)

    try:
        text = await build_schedule_message(
            telegram_id=message.from_user.id,
            target_date=tomorrow,
        )
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: telegram_id=%s, date=%s",
            message.from_user.id,
            tomorrow,
        )
        await message.answer("Не удалось загрузить расписание. Попробуй позже")
        return
    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: telegram_id=%s, date=%s",
            message.from_user.id,
            tomorrow,
        )
        await message.answer("Не удалось обработать расписание. Попробуй позже")
        return

    await message.answer(text, parse_mode="HTML")


@router.message(Command("week"))
@router.message(F.text.in_({"Неделя", "☀️ Неделя"}))
async def command_week(message: Message):
    moscow_tz = timezone(timedelta(hours=3))
    today = datetime.now(moscow_tz).date()

    try:
        text = await build_schedule_message(
            telegram_id=message.from_user.id,
            target_date=today,
            period=7,
        )
    except httpx.HTTPError:
        logger.exception(
            "Ошибка загрузки расписания: telegram_id=%s, date=%s, period=7",
            message.from_user.id,
            today,
        )
        await message.answer("Не удалось загрузить расписание. Попробуй позже")
        return
    except ScheduleParseError:
        logger.exception(
            "Ошибка разбора расписания: telegram_id=%s, date=%s, period=7",
            message.from_user.id,
            today,
        )
        await message.answer("Не удалось обработать расписание. Попробуй позже")
        return

    await message.answer(text, parse_mode="HTML")