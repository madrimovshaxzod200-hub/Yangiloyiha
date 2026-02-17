import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🏢 PlayStation", callback_data="ps")
    kb.button(text="🎤 Karaoke", callback_data="karaoke")
    kb.adjust(1)

    await message.answer(
        "Xush kelibsiz!\nBo‘limni tanlang:",
        reply_markup=kb.as_markup()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())