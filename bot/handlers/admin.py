from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database import db
from filters import IsAdmin
from keyboards.admin_kb import (
    admin_main_menu,
    booking_manage_keyboard
)
from states import AdminStates
from config import config

router = Router()


# =========================================
# ADMIN PANEL
# =========================================
@router.message(F.text == "/admin", IsAdmin())
async def admin_panel(message: Message):
    await message.answer(
        "👨‍💼 Admin panel",
        reply_markup=admin_main_menu()
    )


# =========================================
# YANGI BUYURTMALAR
# =========================================
@router.message(F.text == "📥 Yangi buyurtmalar", IsAdmin())
async def new_bookings(message: Message):
    admin = await db.fetchrow(
        "SELECT section_id FROM admins WHERE telegram_id = $1",
        message.from_user.id
    )

    bookings = await db.fetch("""
        SELECT b.id, u.full_name, un.name as unit_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN units un ON b.unit_id = un.id
        WHERE b.section_id = $1 AND b.status = 'pending'
    """, admin["section_id"])

    if not bookings:
        await message.answer("Yangi buyurtma yo‘q.")
        return

    for booking in bookings:
        await message.answer(
            f"🆔 Booking ID: {booking['id']}\n"
            f"👤 Foydalanuvchi: {booking['full_name']}\n"
            f"🏠 Xona: {booking['unit_name']}",
            reply_markup=booking_manage_keyboard(booking["id"])
        )


# =========================================
# APPROVE
# =========================================
@router.callback_query(F.data.startswith("approve_"), IsAdmin())
async def approve_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[1])

    booking = await db.fetchrow(
        "SELECT unit_id FROM bookings WHERE id = $1",
        booking_id
    )

    # Booking status update
    await db.execute("""
        UPDATE bookings
        SET status = 'approved', approved_at = NOW()
        WHERE id = $1
    """, booking_id)

    # Unitni band qilish
    await db.execute("""
        UPDATE units
        SET is_active = FALSE
        WHERE id = $1
    """, booking["unit_id"])

    await callback.message.edit_text("✅ Buyurtma tasdiqlandi")


# =========================================
# REJECT
# =========================================
@router.callback_query(F.data.startswith("reject_"), IsAdmin())
async def reject_booking(callback: CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[1])

    await state.update_data(booking_id=booking_id)
    await state.set_state(AdminStates.waiting_reject_reason)

    await callback.message.answer("❌ Rad etish sababini yozing:")


# =========================================
# REJECT SABAB QABUL QILISH
# =========================================
@router.message(AdminStates.waiting_reject_reason, IsAdmin())
async def process_reject_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    booking_id = data.get("booking_id")

    booking = await db.fetchrow(
        "SELECT user_id FROM bookings WHERE id = $1",
        booking_id
    )

    # Booking reject qilish
    await db.execute("""
        UPDATE bookings
        SET status = 'rejected',
            reject_reason = $1,
            rejected_at = NOW()
        WHERE id = $2
    """, message.text, booking_id)

    # User fake check +1
    await db.execute("""
        UPDATE users
        SET fake_checks = fake_checks + 1
        WHERE id = $1
    """, booking["user_id"])

    # Fake check sonini tekshirish
    user = await db.fetchrow(
        "SELECT fake_checks FROM users WHERE id = $1",
        booking["user_id"]
    )

    if user["fake_checks"] >= config.MAX_FAKE_CHECKS:
        await db.execute("""
            UPDATE users
            SET is_blocked = TRUE
            WHERE id = $1
        """, booking["user_id"])

    await message.answer("❌ Buyurtma rad etildi")
    await state.clear()