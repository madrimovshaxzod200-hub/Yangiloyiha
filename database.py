import sqlite3
from datetime import datetime

DB_NAME = "bot.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        full_name TEXT,
        username TEXT,
        role TEXT DEFAULT 'user',
        is_blocked INTEGER DEFAULT 0,
        fake_check_count INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    # SECTIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        media_type TEXT,
        media_file_id TEXT,
        payment_card TEXT,
        payment_text TEXT,
        confirm_text TEXT,
        created_by INTEGER
    )
    """)

    # PLACES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_id INTEGER,
        name TEXT,
        description TEXT,
        price INTEGER,
        media_type TEXT,
        media_file_id TEXT,
        status TEXT DEFAULT 'free',
        FOREIGN KEY (section_id) REFERENCES sections (id)
    )
    """)

    # SERVICE ADMIN SECTIONS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS service_admin_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER,
        section_id INTEGER,
        FOREIGN KEY (admin_id) REFERENCES users (id),
        FOREIGN KEY (section_id) REFERENCES sections (id)
    )
    """)

    # BOOKINGS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        section_id INTEGER,
        place_id INTEGER,
        status TEXT,
        receipt_file_id TEXT,
        reject_reason TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (section_id) REFERENCES sections (id),
        FOREIGN KEY (place_id) REFERENCES places (id)
    )
    """)

    conn.commit()
    conn.close()
