from datetime import datetime


# =========================================
# SANANI CHIROYLI FORMAT QILISH
# =========================================
def format_datetime(dt: datetime):
    if not dt:
        return "-"
    return dt.strftime("%d.%m.%Y %H:%M")


# =========================================
# BOOKING TEXT FORMAT
# =========================================
def format_booking_text(booking: dict):
    return (
        f"🆔 Booking ID: {booking.get('id')}\n"
        f"👤 Foydalanuvchi: {booking.get('full_name', '-')}\n"
        f"📱 Telegram ID: {booking.get('telegram_id', '-')}\n"
        f"🏠 Xona: {booking.get('unit_name', '-')}\n"
        f"📌 Status: {booking.get('status', '-')}\n"
        f"📅 Sana: {format_datetime(booking.get('created_at'))}"
    )


# =========================================
# USER MENTION
# =========================================
def user_mention(user_id: int, full_name: str):
    return f"<a href='tg://user?id={user_id}'>{full_name}</a>"


# =========================================
# CALLBACK DATA PARSER
# =========================================
def parse_callback_data(data: str):
    """
    Masalan:
    approve_15
    assign_admin_123456_2
    """
    return data.split("_")


# =========================================
# STATISTIKA TEXT
# =========================================
def format_stats(stats: dict):
    return (
        f"📊 STATISTIKA\n\n"
        f"📦 Jami buyurtmalar: {stats.get('bookings', 0)}\n"
        f"✅ Tasdiqlangan: {stats.get('approved', 0)}\n"
        f"❌ Rad etilgan: {stats.get('rejected', 0)}\n"
        f"⏳ Kutilmoqda: {stats.get('pending', 0)}\n"
        f"👥 Foydalanuvchilar: {stats.get('users', 0)}"
    )


# =========================================
# ODDIY LOGGER
# =========================================
def log(message: str):
    print(f"[LOG {datetime.now().strftime('%H:%M:%S')}] {message}")