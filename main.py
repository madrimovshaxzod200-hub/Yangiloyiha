import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import connect_db
from models import create_tables

# Routers
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from handlers.superadmin import router as superadmin_router


async def main():
    logging.basicConfig(level=logging.INFO)

    # Bot yaratish
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    # Database ulanish
    await connect_db()
    await create_tables()

    print("✅ Database connected")

    # Routerlarni ulash
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(superadmin_router)

    print("🚀 Bot ishga tushdi")

    # Polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())