from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.database import db
from bot.keyboards.user_kb import main_menu, sections_keyboard, units_keyboard
from bot.states import BookingStates
from bot.filters import NotBlocked

router = Router()


# =========================================
# START
# =========================================
@router.message(CommandStart()
async def start_handler(message: Message):
    user = await db.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1",
        message.from_user.id
    )

    if not user:
        await db.execute("""
            INSERT INTO users (telegram_id, full_name, username)
            VALUES ($1, $2, $3)
        """,
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username
        )

    await message.answer(
        "Xush kelibsiz 👋",
        reply_markup=main_menu()
    )


# =========================================
# SECTIONLARNI KO‘RISH
# =========================================
@router.message(F.text == "📂 Bo‘limlar", NotBlocked())
async def show_sections(message: Message, state: FSMContext):
    sections = await db.fetch("SELECT id, name FROM sections")

    if not sections:
        await message.answer("Hozircha bo‘limlar yo‘q.")
        return

    await state.set_state(BookingStates.choosing_section)

    await message.answer(
        "Bo‘limni tanlang:",
        reply_markup=sections_keyboard(sections)
    )


# =========================================
# SECTION TANLASH
# =========================================
@router.callback_query(F.data.startswith("section_"))
async def choose_section(callback: CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[1])

    await state.update_data(section_id=section_id)

    units = await db.fetch("""
        SELECT id, name FROM units
        WHERE section_id = $1 AND is_active = TRUE
    """, section_id)

    if not units:
        await callback.message.answer("Bo‘sh joy yo‘q.")
        return

    await state.set_state(BookingStates.choosing_unit)

    await callback.message.edit_text(
        "Xonani tanlang:",
        reply_markup=units_keyboard(units)
    )


# =========================================
# UNIT TANLASH → BOOKING YARATISH
# =========================================
@router.callback_query(F.data.startswith("unit_"))
async def choose_unit(callback: CallbackQuery, state: FSMContext):
    unit_id = int(callback.data.split("_")[1])
    data = await state.get_data()

    section_id = data.get("section_id")

    user = await db.fetchrow(
        "SELECT id FROM users WHERE telegram_id = $1",
        callback.from_user.id
    )

    booking = await db.fetchrow("""
        INSERT INTO bookings (user_id, section_id, unit_id)
        VALUES ($1, $2, $3)
        RETURNING id
    """,
    user["id"],
    section_id,
    unit_id
    )

    await state.update_data(booking_id=booking["id"])
    await state.set_state(BookingStates.waiting_for_check)

    section = await db.fetchrow(
        "SELECT payment_card, payment_text FROM sections WHERE id = $1",
        section_id
    )

    await callback.message.answer(
        f"💳 To‘lov kartasi:\n{section['payment_card']}\n\n"
        f"{section['payment_text']}\n\n"
        "Chekni rasm qilib yuboring 📸"
    )


# =========================================
# CHEK QABUL QILISH
# =========================================
@router.message(BookingStates.waiting_for_check, F.photo)
async def receive_check(message: Message, state: FSMContext):
    data = await state.get_data()
    booking_id = data.get("booking_id")

    photo = message.photo[-1].file_id

    await db.execute("""
        INSERT INTO payment_checks (booking_id, file_id)
        VALUES ($1, $2)
    """, booking_id, photo)

    await message.answer("Chek qabul qilindi ✅\nAdmin tekshiradi.")

    await state.clear()


# =========================================
# BLOK USER
# =========================================
@router.message()
async def blocked_user(message: Message):
    user = await db.fetchrow(
        "SELECT is_blocked FROM users WHERE telegram_id = $1",
        message.from_user.id
    )

    if user and user["is_blocked"]:
        await message.answer("Siz bloklangansiz ❌")