import os
from dotenv import load_dotenv

# Lokal test uchun .env faylni o‘qiydi
load_dotenv()


class Config:
    def __init__(self):
        # ===============================
        # BOT SETTINGS
        # ===============================
        self.BOT_TOKEN: str = os.getenv("BOT_TOKEN")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable topilmadi!")

        # ===============================
        # DATABASE
        # ===============================
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable topilmadi!")

        # ===============================
        # ADMINS
        # ===============================
        try:
            self.SUPER_ADMIN_ID: int = int(os.getenv("SUPER_ADMIN_ID", "0"))
        except ValueError:
            raise ValueError("SUPER_ADMIN_ID noto‘g‘ri formatda!")

        if self.SUPER_ADMIN_ID == 0:
            raise ValueError("SUPER_ADMIN_ID kiritilmagan!")

        # ===============================
        # SECURITY SETTINGS
        # ===============================
        self.MAX_FAKE_CHECKS: int = 3
        self.BOOKING_TIMEOUT_MINUTES: int = 30

        # ===============================
        # OTHER SETTINGS
        # ===============================
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


config = Config()