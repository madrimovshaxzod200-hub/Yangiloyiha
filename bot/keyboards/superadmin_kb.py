from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =====================================
# SUPER ADMIN ASOSIY MENU (Reply)
# =====================================
def superadmin_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Bo‘lim qo‘shish")],
            [KeyboardButton(text="➕ Xona qo‘shish")],
            [KeyboardButton(text="👤 Admin tayinlash")],
            [KeyboardButton(text="📊 Umumiy statistika")],
            [KeyboardButton(text="⚙ Sozlamalar")]
        ],
        resize_keyboard=True
    )
    return keyboard


# =====================================
# SECTION TANLASH (UNIT QO‘SHISHDA)
# =====================================
def section_select_keyboard(sections: list):
    """
    sections = [{"id": 1, "name": "VIP"}, ...]
    """
    buttons = []

    for section in sections:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=section["name"],
                    callback_data=f"select_section_{section['id']}"
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_superadmin")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =====================================
# ADMIN UCHUN SECTION TANLASH
# =====================================
def admin_section_keyboard(sections: list, telegram_id: int):
    buttons = []

    for section in sections:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=section["name"],
                    callback_data=f"assign_admin_{telegram_id}_{section['id']}"
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_assign")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =====================================
# SOZLAMALAR MENYUSI
# =====================================
def settings_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Botni qayta yuklash",
                    callback_data="restart_bot"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📌 Global sozlama",
                    callback_data="global_settings"
                )
            ]
        ]
    )
    return keyboard