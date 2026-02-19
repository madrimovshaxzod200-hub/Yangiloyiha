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

BOT_TOKEN = "8565639582:AAELDRSjNaqTiLlu0O6_Ksd9D9zFSnzGwOg"
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

@router.message(F.text == "/init_db")
async def init_db(message: Message):
    await db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE;")
    await message.answer("✅ users table yangilandi!")

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

    await message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu(message.from_user.id)
    )


# =========================================
# BLOCK CHECK
# =========================================

async def is_blocked(user_id):
    user = await db.fetchrow(
        "SELECT is_blocked FROM users WHERE telegram_id=$1",
        user_id
    )
    if user and user["is_blocked"]:
        return True
    return False


# =========================================
# BO‘LIMLAR
# =========================================

@dp.message(F.text == "📂 Bo'limlar")
async def show_sections(message: Message):

    if await is_blocked(message.from_user.id):
        await message.answer("❌ Siz bloklangansiz.")
        return

    sections = await db.fetch("SELECT * FROM sections")

    if not sections:
        await message.answer("Hozircha bo‘limlar yo‘q.")
        return

    buttons = []
    for s in sections:
        buttons.append([KeyboardButton(text=f"📁 {s['name']}")])

    buttons.append([KeyboardButton(text="⬅️ Orqaga")])

    kb = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await message.answer("Bo‘limni tanlang:", reply_markup=kb)


# =========================================
# ORQAGA
# =========================================

@dp.message(F.text == "⬅️ Orqaga")
async def back_handler(message: Message):
    user_states.pop(message.from_user.id, None)
    await message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu(message.from_user.id)
    )


# =========================================
# BO‘LIM ICHIGA KIRISH
# =========================================

@dp.message(F.text.startswith("📁 "))
async def open_section(message: Message):

    if await is_blocked(message.from_user.id):
        await message.answer("❌ Siz bloklangansiz.")
        return

    section_name = message.text.replace("📁 ", "")

    section = await db.fetchrow(
        "SELECT * FROM sections WHERE name=$1",
        section_name
    )

    if not section:
        return

    categories = await db.fetch(
        "SELECT * FROM categories WHERE section_id=$1",
        section["id"]
    )

    if not categories:
        await message.answer("Bu bo‘limda kategoriyalar yo‘q.")
        return

    for cat in categories:
        inline = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Band qilish" if not cat["is_booked"] else "❌ Band",
                        callback_data=f"book_{cat['id']}"
                    )
                ]
            ]
        )

        if cat["media_type"] == "photo":
            await message.answer_photo(
                cat["media_file_id"],
                caption=f"{cat['title']}\n\n{cat['description']}",
                reply_markup=inline
            )
        else:
            await message.answer_video(
                cat["media_file_id"],
                caption=f"{cat['title']}\n\n{cat['description']}",
                reply_markup=inline
            )

    await message.answer(
        "⬅️ Orqaga qaytish uchun tugmani bosing",
        reply_markup=back_keyboard()
    )

# =========================================
# BAND QILISH
# =========================================

@dp.callback_query(F.data.startswith("book_"))
async def book_category(callback: CallbackQuery):

    if await is_blocked(callback.from_user.id):
        await callback.message.answer("❌ Siz bloklangansiz.")
        return

    cat_id = int(callback.data.split("_")[1])

    category = await db.fetchrow(
        "SELECT * FROM categories WHERE id=$1",
        cat_id
    )

    if not category:
        return

    if category["is_booked"]:
        await callback.answer("Bu joy band!", show_alert=True)
        return

    section = await db.fetchrow(
        "SELECT * FROM sections WHERE id=$1",
        category["section_id"]
    )

    temp_data[callback.from_user.id] = {
        "category_id": cat_id
    }

    user_states[callback.from_user.id] = "waiting_check"

    text = f"""
💳 To‘lov ma'lumotlari:

{section['payment_text']}

Karta: {section['card_number']}

To‘lovni amalga oshirib chek rasmini yuboring.
"""

    await callback.message.answer(text)
    await callback.answer()


# =========================================
# CHEK QABUL QILISH
# =========================================

@dp.message(F.content_type.in_({ContentType.PHOTO}))
async def receive_check(message: Message):

    if user_states.get(message.from_user.id) != "waiting_check":
        return

    category_id = temp_data[message.from_user.id]["category_id"]

    photo = message.photo[-1].file_id

    await db.execute("""
        INSERT INTO bookings (user_id, category_id, check_file_id)
        VALUES ($1, $2, $3)
    """, message.from_user.id, category_id, photo)

    user_states.pop(message.from_user.id)

    await message.answer(
        "⏳ Arizangiz ko‘rib chiqilmoqda...",
        reply_markup=main_menu(message.from_user.id)
    )

    # ADMIN GA YUBORISH

    category = await db.fetchrow(
        "SELECT * FROM categories WHERE id=$1",
        category_id
    )

    admin = await db.fetchrow(
        "SELECT * FROM admins WHERE section_id=$1",
        category["section_id"]
    )

    if admin:
        inline = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Tasdiqlash",
                        callback_data=f"approve_{category_id}_{message.from_user.id}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Bekor qilish",
                        callback_data=f"reject_{category_id}_{message.from_user.id}"
                    )
                ]
            ]
        )

        await bot.send_photo(
            admin["telegram_id"],
            photo,
            caption=f"""
🆕 Yangi ariza

User ID: {message.from_user.id}
Kategoriya: {category['title']}
""",
            reply_markup=inline
        )

# =========================================
# TASDIQLASH
# =========================================

@dp.callback_query(F.data.startswith("approve_"))
async def approve_booking(callback: CallbackQuery):

    parts = callback.data.split("_")
    category_id = int(parts[1])
    user_id = int(parts[2])

    category = await db.fetchrow(
        "SELECT * FROM categories WHERE id=$1",
        category_id
    )

    admin = await db.fetchrow(
        "SELECT * FROM admins WHERE telegram_id=$1",
        callback.from_user.id
    )

    if not admin or admin["section_id"] != category["section_id"]:
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    # booking approved
    await db.execute("""
        UPDATE bookings
        SET status='approved'
        WHERE user_id=$1 AND category_id=$2 AND status='pending'
    """, user_id, category_id)

    # category band qilish
    await db.execute("""
        UPDATE categories
        SET is_booked=TRUE
        WHERE id=$1
    """, category_id)

    await bot.send_message(
        user_id,
        "✅ Arizangiz tasdiqlandi!"
    )

    await callback.message.edit_caption(
        callback.message.caption + "\n\n✅ TASDIQLANDI"
    )

    await callback.answer("Tasdiqlandi")


# =========================================
# RAD ETISH
# =========================================

@dp.callback_query(F.data.startswith("reject_"))
async def reject_booking(callback: CallbackQuery):

    parts = callback.data.split("_")
    category_id = int(parts[1])
    user_id = int(parts[2])

    category = await db.fetchrow(
        "SELECT * FROM categories WHERE id=$1",
        category_id
    )

    admin = await db.fetchrow(
        "SELECT * FROM admins WHERE telegram_id=$1",
        callback.from_user.id
    )

    if not admin or admin["section_id"] != category["section_id"]:
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    user_states[callback.from_user.id] = f"reject_reason_{category_id}_{user_id}"

    await callback.message.answer("Rad etish sababini yozing:")
    await callback.answer()


@dp.message()
async def handle_reject_reason(message: Message):

    state = user_states.get(message.from_user.id)

    if not state or not state.startswith("reject_reason_"):
        return

    parts = state.split("_")
    category_id = int(parts[2])
    user_id = int(parts[3])

    reason = message.text

    await db.execute("""
        UPDATE bookings
        SET status='rejected', reject_reason=$1
        WHERE user_id=$2 AND category_id=$3 AND status='pending'
    """, reason, user_id, category_id)

    # user rejected_count++
    await db.execute("""
        UPDATE users
        SET rejected_count = rejected_count + 1
        WHERE telegram_id=$1
    """, user_id)

    user = await db.fetchrow(
        "SELECT rejected_count FROM users WHERE telegram_id=$1",
        user_id
    )

    if user["rejected_count"] >= 3:
        await db.execute("""
            UPDATE users SET is_blocked=TRUE WHERE telegram_id=$1
        """, user_id)

        await bot.send_message(
            user_id,
            "❌ 3 marta rad etildingiz. Siz bloklandingiz."
        )
    else:
        await bot.send_message(
            user_id,
            f"❌ Arizangiz rad etildi.\nSabab: {reason}"
        )

    user_states.pop(message.from_user.id)

    await message.answer("Rad etildi.")

# =========================================
# SUPER ADMIN PANEL
# =========================================

@dp.message(F.text == "👑 Super Admin")
async def super_admin_panel(message: Message):

    if message.from_user.id != SUPER_ADMIN_ID:
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Bo‘lim qo‘shish")],
            [KeyboardButton(text="➕ Kategoriya qo‘shish")],
            [KeyboardButton(text="👤 Admin tayinlash")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
        resize_keyboard=True
    )

    await message.answer("Super Admin Panel", reply_markup=kb)


# =========================================
# BO‘LIM QO‘SHISH
# =========================================

@dp.message(F.text == "➕ Bo‘lim qo‘shish")
async def add_section_start(message: Message):

    if message.from_user.id != SUPER_ADMIN_ID:
        return

    user_states[message.from_user.id] = "add_section_name"
    await message.answer("Bo‘lim nomini yuboring:")


@dp.message()
async def add_section_handler(message: Message):

    state = user_states.get(message.from_user.id)

    if state == "add_section_name":
        temp_data[message.from_user.id] = {"name": message.text}
        user_states[message.from_user.id] = "add_section_payment"
        await message.answer("To‘lov matnini yuboring:")
        return

    if state == "add_section_payment":
        temp_data[message.from_user.id]["payment"] = message.text
        user_states[message.from_user.id] = "add_section_card"
        await message.answer("Karta raqamini yuboring:")
        return

    if state == "add_section_card":
        data = temp_data[message.from_user.id]
        await db.execute("""
            INSERT INTO sections (name, payment_text, card_number)
            VALUES ($1, $2, $3)
        """, data["name"], data["payment"], message.text)

        user_states.pop(message.from_user.id)
        await message.answer("✅ Bo‘lim qo‘shildi")
        return


# =========================================
# KATEGORIYA QO‘SHISH
# =========================================

@dp.message(F.text == "➕ Kategoriya qo‘shish")
async def add_category_start(message: Message):

    if message.from_user.id != SUPER_ADMIN_ID:
        return

    sections = await db.fetch("SELECT * FROM sections")

    if not sections:
        await message.answer("Oldin bo‘lim qo‘shing.")
        return

    text = "Bo‘lim ID sini yuboring:\n"
    for s in sections:
        text += f"{s['id']} - {s['name']}\n"

    user_states[message.from_user.id] = "add_cat_section"
    await message.answer(text)


@dp.message()
async def add_category_handler(message: Message):

    state = user_states.get(message.from_user.id)

    if state == "add_cat_section":
        temp_data[message.from_user.id] = {"section_id": int(message.text)}
        user_states[message.from_user.id] = "add_cat_title"
        await message.answer("Kategoriya nomini yuboring:")
        return

    if state == "add_cat_title":
        temp_data[message.from_user.id]["title"] = message.text
        user_states[message.from_user.id] = "add_cat_desc"
        await message.answer("Tavsif yuboring:")
        return

    if state == "add_cat_desc":
        temp_data[message.from_user.id]["desc"] = message.text
        user_states[message.from_user.id] = "add_cat_media"
        await message.answer("Rasm yoki video yuboring:")
        return


@dp.message(F.content_type.in_({ContentType.PHOTO, ContentType.VIDEO}))
async def add_category_media(message: Message):

    if user_states.get(message.from_user.id) != "add_cat_media":
        return

    data = temp_data[message.from_user.id]

    if message.content_type == ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    else:
        file_id = message.video.file_id
        media_type = "video"

    await db.execute("""
        INSERT INTO categories
        (section_id, title, description, media_file_id, media_type)
        VALUES ($1, $2, $3, $4, $5)
    """, data["section_id"], data["title"], data["desc"], file_id, media_type)

    user_states.pop(message.from_user.id)
    await message.answer("✅ Kategoriya qo‘shildi")


# =========================================
# ADMIN TAYINLASH
# =========================================

@dp.message(F.text == "👤 Admin tayinlash")
async def assign_admin(message: Message):

    if message.from_user.id != SUPER_ADMIN_ID:
        return

    user_states[message.from_user.id] = "assign_admin_user"
    await message.answer("Admin qilinadigan user ID ni yuboring:")


@dp.message()
async def assign_admin_handler(message: Message):

    state = user_states.get(message.from_user.id)

    if state == "assign_admin_user":
        temp_data[message.from_user.id] = {"admin_id": int(message.text)}
        user_states[message.from_user.id] = "assign_admin_section"
        await message.answer("Bo‘lim ID ni yuboring:")
        return

    if state == "assign_admin_section":
        data = temp_data[message.from_user.id]

        await db.execute("""
            INSERT INTO admins (telegram_id, section_id)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id)
            DO UPDATE SET section_id=$2
        """, data["admin_id"], int(message.text))

        user_states.pop(message.from_user.id)
        await message.answer("✅ Admin tayinlandi")
        return


# =========================================
# MENING ARIZALARIM
# =========================================

@dp.message(F.text == "📋 Mening arizalarim")
async def my_bookings(message: Message):

    bookings = await db.fetch("""
        SELECT b.*, c.title
        FROM bookings b
        JOIN categories c ON b.category_id=c.id
        WHERE b.user_id=$1
        ORDER BY b.created_at DESC
    """, message.from_user.id)

    if not bookings:
        await message.answer("Arizalar yo‘q.")
        return

    text = "📋 Arizalaringiz:\n\n"

    for b in bookings:
        text += f"{b['title']} - {b['status']}\n"

    await message.answer(text)

# =========================================
# FALLBACK HANDLER
# =========================================

@dp.message()
async def fallback_handler(message: Message):
    print("Kelgan xabar:", message.text)


# =========================================
# MAIN
# =========================================

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

