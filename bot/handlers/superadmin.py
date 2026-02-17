
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards.superadmin import superadmin_main_menu

router = Router()


@router.message(Command("superadmin"))
async def superadmin_panel(message: Message):
    # DB chaqiruv yo‘q
    await message.answer(
        "👑 Super Admin Panel",
        reply_markup=superadmin_main_menu()
    )