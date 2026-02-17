import asyncpg
from bot.config import config

DATABASE_URL = config.DATABASE_URL


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL topilmadi!")
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def close(self):
        await self.pool.close()

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)


db = Database()


# =========================
# TABLE CREATION
# =========================

async def create_tables():

    # USERS
    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        username TEXT,
        full_name TEXT,
        is_banned BOOLEAN DEFAULT FALSE,
        reject_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    await db.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_telegram_id
    ON users(telegram_id);
    """)

    # ADMINS (bo‘lim adminlari)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        section_id INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    # SECTIONS (Bo‘limlar)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS sections (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        media_id TEXT,
        media_type TEXT, -- photo yoki video
        card_number TEXT,
        payment_text TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    # UNITS (Kategoriya / Xona / Joy)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS units (
        id SERIAL PRIMARY KEY,
        section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        description TEXT,
        media_id TEXT,
        media_type TEXT,
        is_busy BOOLEAN DEFAULT FALSE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    await db.execute("""
    CREATE INDEX IF NOT EXISTS idx_units_section
    ON units(section_id);
    """)

    # BOOKINGS (Arizalar)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
        unit_id INTEGER REFERENCES units(id) ON DELETE CASCADE,
        check_file_id TEXT,
        status TEXT DEFAULT 'pending', -- pending / approved / rejected
        admin_id BIGINT,
        reject_reason TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """)

    await db.execute("""
    CREATE INDEX IF NOT EXISTS idx_bookings_user
    ON bookings(user_id);
    """)

    # LOG TABLE (statistika uchun)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS booking_logs (
        id SERIAL PRIMARY KEY,
        booking_id INTEGER,
        action TEXT,
        action_by BIGINT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    print("Database jadvallari yaratildi.")