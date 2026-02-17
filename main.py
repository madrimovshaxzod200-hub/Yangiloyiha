import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ================== Environment Variables ==================
TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID"))

# ================== Data Storage (temporary, SQLite bilan almashtiriladi keyin) ==================
sections = {}  # {'Bo‘lim nomi': {'categories': ['Kat1','Kat2'], 'admin_id': None}}
applications = []  # [{'user_id': , 'section': , 'category': , 'status': 'pending'}]

# ================== Super Admin Menyu ==================
def super_admin_menu():
    keyboard = [
        ["🟢 Bo‘limlarni boshqarish", "🟢 Kategoriyalarni boshqarish"],
        ["🟢 Arizalarni ko‘rish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================== /start komandasi ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == SUPER_ADMIN_ID:
        await update.message.reply_text(
            "Salom Super Admin! Asosiy menyu:", 
            reply_markup=super_admin_menu()
        )
    else:
        await update.message.reply_text("Siz foydalanuvchi sifatida kirishingiz mumkin. Menyu keyin qo‘shiladi.")

# ================== Callback tugmalar ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Bo‘lim qo‘shish (misol)
    if data.startswith("add_section_"):
        section_name = data.replace("add_section_", "")
        if section_name not in sections:
            sections[section_name] = {"categories": [], "admin_id": None}
            await query.edit_message_text(f"Bo‘lim qo‘shildi: {section_name}")
        else:
            await query.edit_message_text("Bu bo‘lim allaqachon mavjud.")
    elif data.startswith("del_section_"):
        section_name = data.replace("del_section_", "")
        if section_name in sections:
            del sections[section_name]
            await query.edit_message_text(f"Bo‘lim o‘chirildi: {section_name}")
        else:
            await query.edit_message_text("Bunday bo‘lim topilmadi.")
    else:
        await query.edit_message_text(f"Siz tugmani bosdingiz: {data}")

# ================== Super Admin Bo‘lim Menyusi ==================
def section_management_menu():
    keyboard = []
    for sec in sections.keys():
        keyboard.append([InlineKeyboardButton(f"❌ {sec}", callback_data=f"del_section_{sec}")])
    keyboard.append([InlineKeyboardButton("➕ Yangi bo‘lim qo‘shish", callback_data="add_section_new")])
    return InlineKeyboardMarkup(keyboard)

# ================== Bot ishga tushirish ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("Bot Railway-ready ishga tushdi...")
app.run_polling()