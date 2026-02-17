from database import db


async def create_tables():
    # ==============================
    # USERS
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        full_name TEXT,
        username TEXT,
        is_blocked BOOLEAN DEFAULT FALSE,
        fake_checks INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ==============================
    # ADMINS
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id BIGSERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        section_id BIGINT REFERENCES sections(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ==============================
    # SECTIONS (Bo‘limlar)
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS sections (
        id BIGSERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        payment_card TEXT,
        payment_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ==============================
    # UNITS (Xona / Joy / Stol / Narsa)
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS units (
        id BIGSERIAL PRIMARY KEY,
        section_id BIGINT REFERENCES sections(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ==============================
    # BOOKINGS
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
        section_id BIGINT REFERENCES sections(id) ON DELETE CASCADE,
        unit_id BIGINT REFERENCES units(id) ON DELETE CASCADE,
        status TEXT DEFAULT 'pending', -- pending, approved, rejected, cancelled
        reject_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP,
        rejected_at TIMESTAMP
    );
    """)

    # ==============================
    # PAYMENT CHECKS
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS payment_checks (
        id BIGSERIAL PRIMARY KEY,
        booking_id BIGINT REFERENCES bookings(id) ON DELETE CASCADE,
        file_id TEXT,
        is_valid BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ==============================
    # SETTINGS (Global)
    # ==============================
    await db.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id BIGSERIAL PRIMARY KEY,
        key TEXT UNIQUE,
        value TEXT
    );
    """)