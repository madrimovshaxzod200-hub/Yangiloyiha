from database import db


# =========================================
# ADMIN SECTIONINI OLISH
# =========================================
async def get_admin_section(telegram_id: int):
    admin = await db.fetchrow("""
        SELECT section_id
        FROM admins
        WHERE telegram_id = $1
    """, telegram_id)

    if not admin:
        return None

    return admin["section_id"]


# =========================================
# PENDING BOOKINGLAR (SECTION BO‘YICHA)
# =========================================
async def get_pending_bookings(section_id: int):
    bookings = await db.fetch("""
        SELECT b.id,
               u.full_name,
               u.telegram_id,
               un.name AS unit_name
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN units un ON b.unit_id = un.id
        WHERE b.section_id = $1
        AND b.status = 'pending'
        ORDER BY b.created_at ASC
    """, section_id)

    return bookings


# =========================================
# BOOKINGNI TOPISH
# =========================================
async def get_booking(booking_id: int):
    booking = await db.fetchrow("""
        SELECT *
        FROM bookings
        WHERE id = $1
    """, booking_id)

    return booking


# =========================================
# UNITNI MANUAL BAND QILISH
# =========================================
async def deactivate_unit(unit_id: int):
    await db.execute("""
        UPDATE units
        SET is_active = FALSE
        WHERE id = $1
    """, unit_id)


# =========================================
# UNITNI MANUAL BO‘SH QILISH
# =========================================
async def activate_unit(unit_id: int):
    await db.execute("""
        UPDATE units
        SET is_active = TRUE
        WHERE id = $1
    """, unit_id)


# =========================================
# ADMIN STATISTIKASI
# =========================================
async def get_admin_stats(section_id: int):

    total = await db.fetchval("""
        SELECT COUNT(*)
        FROM bookings
        WHERE section_id = $1
    """, section_id)

    approved = await db.fetchval("""
        SELECT COUNT(*)
        FROM bookings
        WHERE section_id = $1
        AND status = 'approved'
    """, section_id)

    rejected = await db.fetchval("""
        SELECT COUNT(*)
        FROM bookings
        WHERE section_id = $1
        AND status = 'rejected'
    """, section_id)

    pending = await db.fetchval("""
        SELECT COUNT(*)
        FROM bookings
        WHERE section_id = $1
        AND status = 'pending'
    """, section_id)

    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }