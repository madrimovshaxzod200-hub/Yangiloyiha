import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from bot.config import config
from bot.database import connect_db
from bot.models import create_tables

from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router
from bot.handlers.superadmin import router as superadmin_router


async def main():
    # =========================
    # LOGGING
    # =========================
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    logging.info("Bot ishga tushmoqda...")

    # =========================
    # DATABASE CONNECT
    # =========================
    await connect_db()
    await create_tables()
    logging.info("Database ulandi va jadvallar tayyor.")

    # =========================
    # BOT INIT
    # =========================
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    # =========================
    # DISPATCHER
    # =========================
    dp = Dispatcher(storage=MemoryStorage())

    # Routers
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(superadmin_router)

    logging.info("Routerlar ulandi. Polling boshlanmoqda...")

    # =========================
    # START POLLING
    # =========================
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")