import asyncio
import logging
import os
import asyncpg

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ContentType

# =========================================
# CONFIG
# =========================================

BOT_TOKEN = "8565639582:AAELDRSjNaqTiLlu0O6_Ksd9D9zFSnzGwOg"
SUPER_ADMIN_ID = 6780565815  # O'ZINGNI ID

DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
db = None


# =========================================
# DATABASE
# =========================================

async def init_db():
    global db
    db = await asyncpg.connect(DATABASE_URL)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id BIGINT PRIMARY KEY,
        rejected_count INTEGER DEFAULT 0,
        is_blocked BOOLEAN DEFAULT FALSE
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS sections (
        id SERIAL PRIMARY KEY,
        name TEXT,
        payment_text TEXT,
        card_number TEXT
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        section_id INTEGER REFERENCES sections(id),
        title TEXT,
        description TEXT,
        media_file_id TEXT,
        is_booked BOOLEAN DEFAULT FALSE
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        category_id INTEGER,
        check_file_id TEXT,
        status TEXT DEFAULT 'pending',
        reject_reason TEXT
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        telegram_id BIGINT PRIMARY KEY,
        section_id INTEGER
    );
    """)


# =========================================
# START
# =========================================

@dp.message(Command("start"))
async def start_handler(message: Message):
    user = await db.fetchrow(
        "SELECT * FROM users WHERE telegram_id=$1",
        message.from_user.id
    )

    if not user:
        await db.execute(
            "INSERT INTO users (telegram_id) VALUES ($1)",
            message.from_user.id
        )

    kb = ReplyKeyboardBuilder()
    kb.button(text="📂 Bo'limlar")
    kb.button(text="📋 Mening arizalarim")

    if message.from_user.id == SUPER_ADMIN_ID:
        kb.button(text="👑 Super Admin")

    kb.adjust(1)

    await message.answer(
        "Asosiy menyu:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


# =========================================
# SECTIONS
# =========================================

@dp.message(F.text == "📂 Bo'limlar")
async def show_sections(message: Message):
    sections = await db.fetch("SELECT * FROM sections")

    if not sections:
        await message.answer("Hozircha bo‘limlar yo‘q.")
        return

    kb = ReplyKeyboardBuilder()

    for s in sections:
        kb.button(text=s["name"])

    kb.button(text="⬅️ Orqaga")
    kb.adjust(1)

    await message.answer(
        "Bo‘limni tanlang:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


# =========================================
# BACK
# =========================================

@dp.message(F.text == "⬅️ Orqaga")
async def back_handler(message: Message):
    await start_handler(message)


# =========================================
# SUPER ADMIN PANEL
# =========================================

@dp.message(F.text == "👑 Super Admin")
async def super_admin_panel(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        return

    kb = ReplyKeyboardBuilder()
    kb.button(text="➕ Bo‘lim qo‘shish")
    kb.button(text="📋 Bo‘limlar ro‘yxati")
    kb.button(text="⬅️ Orqaga")
    kb.adjust(1)

    await message.answer(
        "Super Admin Panel",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


# =========================================
# ADD SECTION
# =========================================

adding_section = {}

@dp.message(F.text == "➕ Bo‘lim qo‘shish")
async def add_section_start(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        return

    adding_section[message.from_user.id] = {}
    await message.answer("Bo‘lim nomini yuboring:")


@dp.message()
async def handle_add_section(message: Message):
    if message.from_user.id in adding_section:
        data = adding_section[message.from_user.id]

        if "name" not in data:
            data["name"] = message.text
            await message.answer("To‘lov matnini yuboring:")
            return

        if "payment_text" not in data:
            data["payment_text"] = message.text
            await message.answer("Karta raqamini yuboring:")
            return

        if "card_number" not in data:
            data["card_number"] = message.text

            await db.execute("""
                INSERT INTO sections (name, payment_text, card_number)
                VALUES ($1, $2, $3)
            """, data["name"], data["payment_text"], data["card_number"])

            del adding_section[message.from_user.id]

            await message.answer("Bo‘lim qo‘shildi ✅")
            return


# =========================================
# MAIN
# =========================================

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())