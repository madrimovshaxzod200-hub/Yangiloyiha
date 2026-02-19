import asyncio
import logging
import os
import asyncpg
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.enums import ContentType


# =========================================
# CONFIG
# =========================================

BOT_TOKEN = "8565639582:AAELDRSjNaqTiLlu0O6_Ksd9D9zFSnzGwOg""
SUPER_ADMIN_ID = 6780565815  # O'ZINGNI ID

DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
db = None


# =========================================
# GLOBAL STATES (oddiy dict FSM)
# =========================================

user_states = {}
temp_data = {}


# =========================================
# DATABASE INIT
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
        media_type TEXT,
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
        reject_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        telegram_id BIGINT PRIMARY KEY,
        section_id INTEGER
    );
    """)


# =========================================
# KEYBOARDS
# =========================================

def main_menu(user_id):
    buttons = [
        [KeyboardButton(text="📂 Bo'limlar")],
        [KeyboardButton(text="📋 Mening arizalarim")]
    ]

    if user_id == SUPER_ADMIN_ID:
        buttons.append([KeyboardButton(text="👑 Super Admin")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


def back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True
    )