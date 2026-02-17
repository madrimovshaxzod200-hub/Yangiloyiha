from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =====================================
# ASOSIY MENU (Reply Keyboard)
# =====================================
def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Bo‘limlar")],
            [KeyboardButton(text="📄 Mening buyurtmalarim")]
        ],
        resize_keyboard=True
    )
    return keyboard


# =====================================
# SECTIONLAR (Inline)
# =====================================
def sections_keyboard(sections: list):
    """
    sections = [(id, name), (id, name)]
    """
    buttons = []

    for section in sections:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=section["name"],
                    callback_data=f"section_{section['id']}"
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =====================================
# UNITLAR (Xonalar)
# =====================================
def units_keyboard(units: list):
    """
    units = [(id, name)]
    """
    buttons = []

    for unit in units:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=unit["name"],
                    callback_data=f"unit_{unit['id']}"
                )
            ]
        )

    buttons.append(
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_sections")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =====================================
# BOOKING CONFIRMATION
# =====================================
def booking_confirm_keyboard(booking_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=f"cancel_{booking_id}"
                )
            ]
        ]
    )
    return keyboard