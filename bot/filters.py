from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import config
from bot.database import db


# ==============================
# SUPER ADMIN FILTER
# ==============================
class IsSuperAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id
        return user_id == config.SUPER_ADMIN_ID


# ==============================
# ADMIN FILTER
# ==============================
class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id

        admin = await db.fetchrow(
            "SELECT * FROM admins WHERE telegram_id = $1",
            user_id
        )

        return bool(admin)


# ==============================
# SECTION ADMIN FILTER
# (Admin faqat o‘z sectionini boshqaradi)
# ==============================
class IsSectionAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id

        admin = await db.fetchrow(
            "SELECT section_id FROM admins WHERE telegram_id = $1",
            user_id
        )

        if not admin:
            return False

        return True


# ==============================
# USER BLOCK FILTER
# ==============================
class NotBlocked(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id

        user = await db.fetchrow(
            "SELECT is_blocked FROM users WHERE telegram_id = $1",
            user_id
        )

        if not user:
            return True  # yangi user

        return not user["is_blocked"]