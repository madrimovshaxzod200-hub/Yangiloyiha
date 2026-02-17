from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# =====================================
# ADMIN ASOSIY MENU (Reply)
# =====================================
def admin_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Yangi buyurtmalar")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    return keyboard


# =====================================
# BOOKING BOSHQARISH (Inline)
# =====================================
def booking_manage_keyboard(booking_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve_{booking_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=f"reject_{booking_id}"
                )
            ]
        ]
    )
    return keyboard


# =====================================
# REJECT TASDIQ (Sabab yozishdan oldin)
# =====================================
def reject_confirm_keyboard(booking_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✍ Sabab yozish",
                    callback_data=f"write_reason_{booking_id}"
                )
            ]
        ]
    )
    return keyboard


# =====================================
# UNIT HOLAT BOSHQARISH
# =====================================
def unit_manage_keyboard(unit_id: int, is_active: bool):
    if is_active:
        button = InlineKeyboardButton(
            text="🔒 Band qilish",
            callback_data=f"deactivate_unit_{unit_id}"
        )
    else:
        button = InlineKeyboardButton(
            text="🔓 Bo‘shatish",
            callback_data=f"activate_unit_{unit_id}"
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button]]
    )

    return keyboard


# =====================================
# STATISTIKA TUGMALARI
# =====================================
def stats_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Bugungi",
                    callback_data="stats_today"
                ),
                InlineKeyboardButton(
                    text="📆 Oylik",
                    callback_data="stats_month"
                )
            ]
        ]
    )
    return keyboard