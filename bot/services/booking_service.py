from database import db
from config import config


# =========================================
# BOOKING YARATISH
# =========================================
async def create_booking(user_id: int, section_id: int, unit_id: int):
    booking = await db.fetchrow("""
        INSERT INTO bookings (user_id, section_id, unit_id)
        VALUES ($1, $2, $3)
        RETURNING *
    """, user_id, section_id, unit_id)

    return booking


# =========================================
# CHEK SAQLASH
# =========================================
async def save_payment_check(booking_id: int, file_id: str):
    await db.execute("""
        INSERT INTO payment_checks (booking_id, file_id)
        VALUES ($1, $2)
    """, booking_id, file_id)


# =========================================
# BOOKING APPROVE
# =========================================
async def approve_booking(booking_id: int):
    booking = await db.fetchrow(
        "SELECT unit_id FROM bookings WHERE id = $1",
        booking_id
    )

    if not booking:
        return False

    # Booking status update
    await db.execute("""
        UPDATE bookings
        SET status = 'approved',
            approved_at = NOW()
        WHERE id = $1
    """, booking_id)

    # Unitni band qilish
    await db.execute("""
        UPDATE units
        SET is_active = FALSE
        WHERE id = $1
    """, booking["unit_id"])

    return True


# =========================================
# BOOKING REJECT
# =========================================
async def reject_booking(booking_id: int, reason: str):
    booking = await db.fetchrow("""
        SELECT user_id, unit_id
        FROM bookings
        WHERE id = $1
    """, booking_id)

    if not booking:
        return False

    # Bookingni reject qilish
    await db.execute("""
        UPDATE bookings
        SET status = 'rejected',
            reject_reason = $1,
            rejected_at = NOW()
        WHERE id = $2
    """, reason, booking_id)

    # Fake check +1
    await db.execute("""
        UPDATE users
        SET fake_checks = fake_checks + 1
        WHERE id = $1
    """, booking["user_id"])

    # Fake check tekshirish
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

    return True


# =========================================
# UNITNI BO‘SH QILISH
# =========================================
async def release_unit(unit_id: int):
    await db.execute("""
        UPDATE units
        SET is_active = TRUE
        WHERE id = $1
    """, unit_id)


# =========================================
# USER BLOCKNI TEKSHIRISH
# =========================================
async def is_user_blocked(telegram_id: int):
    user = await db.fetchrow("""
        SELECT is_blocked
        FROM users
        WHERE telegram_id = $1
    """, telegram_id)

    if not user:
        return False

    return user["is_blocked"]