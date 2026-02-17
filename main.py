import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
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

# ================== Super Admin reply keyboard ==================
def super_admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🟢 Bo‘limlarni boshqarish"))
    keyboard.add(KeyboardButton("🟢 Kategoriyalarni boshqarish"))
    keyboard.add(KeyboardButton("🟢 Arizalarni ko‘rish"))
    return keyboard

# ================== START COMMAND ==================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    if message.from_user.id == SUPER_ADMIN_ID:
        await message.answer("Salom Super Admin! Asosiy menyu:", reply_markup=super_admin_menu())
    else:
        await message.answer("Siz foydalanuvchi sifatida kirishingiz mumkin. Keyin foydalanuvchi menyusi qo‘shiladi.")

# ================== SECTION MANAGEMENT MENU ==================
def section_management_menu():
    keyboard = InlineKeyboardMarkup()
    for sec in sections.keys():
        keyboard.add(
            InlineKeyboardButton(f"❌ {sec}", callback_data=f"del_section:{sec}"),
            InlineKeyboardButton(f"👤 Admin tayinlash", callback_data=f"assign_admin:{sec}")
        )
    keyboard.add(InlineKeyboardButton("➕ Yangi bo‘lim qo‘shish", callback_data="add_section"))
    return keyboard

# ================== CATEGORY MANAGEMENT MENU ==================
def category_management_menu(section_name):
    keyboard = InlineKeyboardMarkup()
    if section_name in sections:
        for cat in sections[section_name]["categories"]:
            keyboard.add(
                InlineKeyboardButton(f"❌ {cat}", callback_data=f"del_category:{section_name}:{cat}")
            )
        keyboard.add(
            InlineKeyboardButton("➕ Yangi kategoriya qo‘shish", callback_data=f"add_category:{section_name}")
        )
    return keyboard

# ================== HANDLER FOR TEXT BUTTONS ==================
@dp.message(F.text == "🟢 Bo‘limlarni boshqarish")
async def show_sections(message: types.Message):
    if not sections:
        await message.answer("Hozircha bo‘limlar mavjud emas.")
    await message.answer("Bo‘lim boshqaruv paneli:", reply_markup=section_management_menu())

@dp.message(F.text == "🟢 Kategoriyalarni boshqarish")
async def choose_section_for_category(message: types.Message):
    if not sections:
        await message.answer("Hozircha bo‘limlar mavjud emas.")
        return
    keyboard = InlineKeyboardMarkup()
    for sec in sections.keys():
        keyboard.add(
            InlineKeyboardButton(sec, callback_data=f"manage_category:{sec}")
        )
    await message.answer("Kategoriya boshqarish uchun bo‘limni tanlang:", reply_markup=keyboard)

# ================== CALLBACK QUERIES ==================
@dp.callback_query()
async def handle_callbacks(call: types.CallbackQuery):
    data = call.data

    # ----- Add section -----
    if data == "add_section":
        await call.message.answer("Yangi bo‘lim nomini yuboring:")

        @dp.message()
        async def receive_new_section(msg: types.Message):
            sec_name = msg.text.strip()
            if sec_name in sections:
                await msg.answer("Bu bo‘lim allaqachon mavjud.")
            else:
                sections[sec_name] = {"categories": [], "admin_id": None}
                await msg.answer(f"Bo‘lim qo‘shildi: {sec_name}")
            dp.message_handlers.pop()  # remove temporary listener
        await call.answer()

    # ----- Delete section -----
    elif data.startswith("del_section:"):
        sec = data.split(":")[1]
        if sec in sections:
            del sections[sec]
            await call.message.answer(f"Bo‘lim o‘chirildi: {sec}")
        else:
            await call.message.answer("Bunday bo‘lim topilmadi!")
        await call.answer()

    # ----- Assign admin -----
    elif data.startswith("assign_admin:"):
        sec = data.split(":")[1]
        await call.message.answer(f"{sec} bo‘limi uchun admin ID yuboring:")

        @dp.message()
        async def assign_admin(msg: types.Message):
            try:
                admin_id = int(msg.text.strip())
                sections[sec]["admin_id"] = admin_id
                await msg.answer(f"Admin tayinlandi: {admin_id} bo‘lim {sec}")
            except ValueError:
                await msg.answer("Iltimos, to‘g‘ri raqam kiriting.")
            dp.message_handlers.pop()
        await call.answer()

    # ----- Manage category -----
    elif data.startswith("manage_category:"):
        sec = data.split(":")[1]
        await call.message.answer(f"{sec} bo‘lim kategoriyalari:", reply_markup=category_management_menu(sec))
        await call.answer()

    # ----- Add category -----
    elif data.startswith("add_category:"):
        sec = data.split(":")[1]
        await call.message.answer("Yangi kategoriya nomini yuboring:")

        @dp.message()
        async def add_category(msg: types.Message):
            cat_name = msg.text.strip()
            if cat_name in sections[sec]["categories"]:
                await msg.answer("Bu kategoriya allaqachon mavjud.")
            else:
                sections[sec]["categories"].append(cat_name)
                await msg.answer(f"Kategoriya qo‘shildi: {cat_name}")
            dp.message_handlers.pop()
        await call.answer()

    # ----- Delete category -----
    elif data.startswith("del_category:"):
        parts = data.split(":")
        sec = parts[1]
        cat = parts[2]
        if cat in sections[sec]["categories"]:
            sections[sec]["categories"].remove(cat)
            await call.message.answer(f"Kategoriya o‘chirildi: {cat}")
        await call.answer()

    else:
        await call.answer("Nomaʼlum tugma!")

# ================== RUN BOT ==================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())