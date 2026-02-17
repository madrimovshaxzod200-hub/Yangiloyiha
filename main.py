import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

# ================== Environment variables ==================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================== Temporary storage ==================
sections = {}  # {'Bo‘lim nomi': {'categories': [], 'admin_id': None}}
applications = []  # [{'user_id': , 'section': , 'category': , 'status': 'pending'}]

# ================== Super Admin menyusi ==================
def super_admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🟢 Bo‘limlarni boshqarish"))
    keyboard.add(KeyboardButton("🟢 Kategoriyalarni boshqarish"))
    keyboard.add(KeyboardButton("🟢 Arizalarni ko‘rish"))
    return keyboard

# ================== /start komandasi ==================
@dp.message(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id == SUPER_ADMIN_ID:
        await message.answer("Salom Super Admin! Asosiy menyu:", reply_markup=super_admin_menu())
    else:
        await message.answer("Siz foydalanuvchi sifatida kirishingiz mumkin. Menyu keyin qo‘shiladi.")

# ================== Inline tugma yaratish ==================
def section_management_menu():
    keyboard = InlineKeyboardMarkup()
    for sec in sections.keys():
        keyboard.add(InlineKeyboardButton(f"❌ {sec}", callback_data=f"del_section_{sec}"))
    keyboard.add(InlineKeyboardButton("➕ Yangi bo‘lim qo‘shish", callback_data="add_section_new"))
    return keyboard

# ================== Callback query ==================
@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    data = call.data
    if data.startswith("add_section_"):
        section_name = data.replace("add_section_", "")
        if section_name not in sections:
            sections[section_name] = {"categories": [], "admin_id": None}
            await call.message.edit_text(f"Bo‘lim qo‘shildi: {section_name}")
        else:
            await call.message.edit_text("Bu bo‘lim allaqachon mavjud.")
    elif data.startswith("del_section_"):
        section_name = data.replace("del_section_", "")
        if section_name in sections:
            del sections[section_name]
            await call.message.edit_text(f"Bo‘lim o‘chirildi: {section_name}")
        else:
            await call.message.edit_text("Bunday bo‘lim topilmadi.")
    else:
        await call.message.edit_text(f"Siz tugmani bosdingiz: {data}")
    await call.answer()

# ================== Bot ishga tushirish ==================
async def main():
    dp.startup.register(lambda _: print("Bot ishga tushdi..."))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())