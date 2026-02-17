from bot.database import db


# =========================================
# SECTION YARATISH
# =========================================
async def create_section(name: str, card: str, payment_text: str):
    section = await db.fetchrow("""
        INSERT INTO sections (name, payment_card, payment_text)
        VALUES ($1, $2, $3)
        RETURNING *
    """, name, card, payment_text)

    return section


# =========================================
# SECTIONLARNI OLISH
# =========================================
async def get_all_sections():
    sections = await db.fetch("""
        SELECT id, name
        FROM sections
        ORDER BY created_at DESC
    """)
    return sections


# =========================================
# BITTA SECTIONNI OLISH
# =========================================
async def get_section(section_id: int):
    section = await db.fetchrow("""
        SELECT *
        FROM sections
        WHERE id = $1
    """, section_id)

    return section


# =========================================
# UNIT QO‘SHISH
# =========================================
async def create_unit(section_id: int, name: str):
    unit = await db.fetchrow("""
        INSERT INTO units (section_id, name)
        VALUES ($1, $2)
        RETURNING *
    """, section_id, name)

    return unit


# =========================================
# SECTION BO‘YICHA UNITLAR
# =========================================
async def get_units_by_section(section_id: int):
    units = await db.fetch("""
        SELECT id, name, is_active
        FROM units
        WHERE section_id = $1
        ORDER BY created_at DESC
    """, section_id)

    return units


# =========================================
# ADMIN TAYINLASH
# =========================================
async def assign_admin(telegram_id: int, section_id: int):
    await db.execute("""
        INSERT INTO admins (telegram_id, section_id)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id)
        DO UPDATE SET section_id = EXCLUDED.section_id
    """, telegram_id, section_id)


# =========================================
# GLOBAL STATISTIKA
# =========================================
async def get_global_stats():
    total_users = await db.fetchval("SELECT COUNT(*) FROM users")
    total_bookings = await db.fetchval("SELECT COUNT(*) FROM bookings")
    approved = await db.fetchval("""
        SELECT COUNT(*) FROM bookings WHERE status = 'approved'
    """)
    rejected = await db.fetchval("""
        SELECT COUNT(*) FROM bookings WHERE status = 'rejected'
    """)
    pending = await db.fetchval("""
        SELECT COUNT(*) FROM bookings WHERE status = 'pending'
    """)

    return {
        "users": total_users,
        "bookings": total_bookings,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }