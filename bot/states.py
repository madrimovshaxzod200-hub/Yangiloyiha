from aiogram.fsm.state import StatesGroup, State


# =====================================
# USER BOOKING STATES
# =====================================
class BookingStates(StatesGroup):

    # Section tanlash
    choosing_section = State()

    # Unit (xona / joy) tanlash
    choosing_unit = State()

    # To‘lov chekini yuborish
    waiting_for_check = State()

    # Bekor qilish sababi (agar kerak bo‘lsa)
    cancelling_booking = State()


# =====================================
# ADMIN STATES
# =====================================
class AdminStates(StatesGroup):

    # Reject sabab yozish
    waiting_reject_reason = State()


# =====================================
# SUPER ADMIN STATES
# =====================================
class SuperAdminStates(StatesGroup):

    # Section yaratish
    waiting_section_name = State()
    waiting_section_card = State()
    waiting_section_payment_text = State()

    # Unit yaratish
    waiting_unit_section = State()
    waiting_unit_name = State()

    # Admin tayinlash
    waiting_admin_telegram_id = State()
    waiting_admin_section = State()