import os
from dotenv import load_dotenv

# .env fayl bo‘lsa o‘qiydi (lokal test uchun)
load_dotenv()


class Config:
    # ===============================
    # BOT SETTINGS
    # ===============================
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")

    # ===============================
    # DATABASE
    # ===============================
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # ===============================
    # ADMINS
    # ===============================
    SUPER_ADMIN_ID: int = int(os.getenv("SUPER_ADMIN_ID", "0"))

    # ===============================
    # SECURITY SETTINGS
    # ===============================
    MAX_FAKE_CHECKS: int = 3   # 3 ta noto‘g‘ri chekdan keyin block
    BOOKING_TIMEOUT_MINUTES: int = 30  # Chek yuborish vaqti

    # ===============================
    # OTHER SETTINGS
    # ===============================
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"


config = Config()