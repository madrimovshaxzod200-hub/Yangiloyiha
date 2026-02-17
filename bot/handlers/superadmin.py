from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database import db
from bot.filters import IsSuperAdmin
from bot.keyboards.superadmin_kb import (
    superadmin_main_menu,
    section_select_keyboard,
    admin_section_keyboard
)
from bot.states import SuperAdminStates

router = Router()


# =========================================
# SUPER ADMIN PANEL
# =========================================
@router.message(F.text == "superadmin", IsSuperAdmin())
async def superadmin_panel(message: Message):
    await message.answer(
        "👑 Super Admin Panel",
        reply_markup=superadmin_main_menu()
    )


# =========================================
# SECTION QO‘SHISH
# =========================================
@router.message(F.text == "➕ Bo‘lim qo‘shish", IsSuperAdmin())
async def add_section_start(message: Message, state: FSMContext):
    await state.set_state(SuperAdminStates.waiting_section_name)
    await message.answer("Bo‘lim nomini kiriting:")


@router.message(SuperAdminStates.waiting_section_name, IsSuperAdmin())
async def add_section_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(SuperAdminStates.waiting_section_card)
    await message.answer("To‘lov kartasini kiriting:")


@router.message(SuperAdminStates.waiting_section_card, IsSuperAdmin())
async def add_section_card(message: Message, state: FSMContext):
    await state.update_data(card=message.text)
    await state.set_state(SuperAdminStates.waiting_section_payment_text)
    await message.answer("To‘lov matnini kiriting:")


@router.message(SuperAdminStates.waiting_section_payment_text, IsSuperAdmin())
async def save_section(message: Message, state: FSMContext):
    data = await state.get_data()

    await db.execute("""
        INSERT INTO sections (name, payment_card, payment_text)
        VALUES ($1, $2, $3)
    """,
    data["name"],
    data["card"],
    message.text
    )

    await message.answer("✅ Bo‘lim yaratildi")
    await state.clear()


# =========================================
# UNIT QO‘SHISH
# =========================================
@router.message(F.text == "➕ Xona qo‘shish", IsSuperAdmin())
async def add_unit_start(message: Message):
    sections = await db.fetch("SELECT id, name FROM sections")

    if not sections:
        await message.answer("Avval bo‘lim yarating.")
        return

    await message.answer(
        "Bo‘limni tanlang:",
        reply_markup=section_select_keyboard(sections)
    )


@router.callback_query(F.data.startswith("select_section_"), IsSuperAdmin())
async def select_section(callback: CallbackQuery, state: FSMContext):
    section_id = int(callback.data.split("_")[2])

    await state.update_data(section_id=section_id)
    await state.set_state(SuperAdminStates.waiting_unit_name)

    await callback.message.answer("Xona nomini kiriting:")


@router.message(SuperAdminStates.waiting_unit_name, IsSuperAdmin())
async def save_unit(message: Message, state: FSMContext):
    data = await state.get_data()

    await db.execute("""
        INSERT INTO units (section_id, name)
        VALUES ($1, $2)
    """,
    data["section_id"],
    message.text
    )

    await message.answer("✅ Xona qo‘shildi")
    await state.clear()


# =========================================
# ADMIN TAYINLASH
# =========================================
@router.message(F.text == "👤 Admin tayinlash", IsSuperAdmin())
async def assign_admin_start(message: Message, state: FSMContext):
    await state.set_state(SuperAdminStates.waiting_admin_telegram_id)
    await message.answer("Admin qilmoqchi bo‘lgan Telegram ID ni kiriting:")


@router.message(SuperAdminStates.waiting_admin_telegram_id, IsSuperAdmin())
async def choose_admin_section(message: Message, state: FSMContext):
    telegram_id = int(message.text)
    await state.update_data(telegram_id=telegram_id)

    sections = await db.fetch("SELECT id, name FROM sections")

    await message.answer(
        "Admin qaysi bo‘limga biriktiriladi?",
        reply_markup=admin_section_keyboard(sections, telegram_id)
    )


@router.callback_query(F.data.startswith("assign_admin_"), IsSuperAdmin())
async def save_admin(callback: CallbackQuery):
    parts = callback.data.split("_")
    telegram_id = int(parts[2])
    section_id = int(parts[3])

    await db.execute("""
        INSERT INTO admins (telegram_id, section_id)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id) DO UPDATE
        SET section_id = EXCLUDED.section_id
    """,
    telegram_id,
    section_id
    )

    await callback.message.edit_text("✅ Admin tayinlandi")


# =========================================
# UMUMIY STATISTIKA
# =========================================
@router.message(F.text == "📊 Umumiy statistika", IsSuperAdmin())
async def global_stats(message: Message):
    total_users = await db.fetchval("SELECT COUNT(*) FROM users")
    total_bookings = await db.fetchval("SELECT COUNT(*) FROM bookings")
    approved = await db.fetchval(
        "SELECT COUNT(*) FROM bookings WHERE status = 'approved'"
    )

    await message.answer(
        f"👥 Foydalanuvchilar: {total_users}\n"
        f"📦 Buyurtmalar: {total_bookings}\n"
        f"✅ Tasdiqlangan: {approved}"
    )


# =========================================
# USER UNBLOCK
# =========================================
@router.message(F.text.startswith("/unblock"), IsSuperAdmin())
async def unblock_user(message: Message):
    try:
        telegram_id = int(message.text.split()[1])
    except:
        await message.answer("Format: /unblock 123456789")
        return

    await db.execute("""
        UPDATE users
        SET is_blocked = FALSE,
            fake_checks = 0
        WHERE telegram_id = $1
    """, telegram_id)

    await message.answer("✅ User unblock qilindi")