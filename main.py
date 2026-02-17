import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.database import connect_db
from bot.models import create_tables

from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router
from bot.handlers.superadmin import router as superadmin_router


async def main():
    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    logging.info("Bot ishga tushmoqda...")

    # DB ulanish
    await connect_db()
    await create_tables()
    logging.info("Database ulandi va tablelar tayyor.")

    # Bot
    bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
    )

    # Dispatcher
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(superadmin_router)

    logging.info("Routerlar ulandi. Polling boshlanmoqda...")

    # Polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")