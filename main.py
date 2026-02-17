import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

# 📌 Environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📌 Temporary storage
sections = {}  # {'Bo‘lim nomi': {'categories': [], 'admin_id': None}}


# 📌 Super admin reply keyboard
def super_admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🟢 Bo‘limlarni boshqarish"))
    keyboard.add(KeyboardButton("🟢 Kategoriyalarni boshqarish"))
    keyboard.add(KeyboardButton("🟢 Arizalarni ko‘rish"))
    return keyboard


# ================= START COMMAND =================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    if message.from_user.id == SUPER_ADMIN_ID:
        await message.answer("Salom Super Admin! Asosiy menyu:", reply_markup=super_admin_menu())
    else:
        await message.answer("Siz foydalanuvchi sifatida kirishingiz mumkin. Keyin foydalanuvchi menyusi qo‘shiladi.")


# ================= INLINE BUTTONS MENU =================
def section_management_menu():
    keyboard = InlineKeyboardMarkup()
    for sec in sections.keys():
        keyboard.add(InlineKeyboardButton(f"❌ {sec}", callback_data=f"del_section:{sec}"))
    keyboard.add(InlineKeyboardButton("➕ Yangi bo‘lim qo‘shish", callback_data="add_section"))
    return keyboard


# ================= HANDLER FOR TEXT BUTTONS =================
@dp.message(F.text == "🟢 Bo‘limlarni boshqarish")
async def show_sections(message: types.Message):
    await message.answer("Bo‘lim boshqaruv paneli:", reply_markup=None, 
                         reply_markup=section_management_menu())


# ================= CALLBACK QUERIES =================
@dp.callback_query()
async def handle_callbacks(call: types.CallbackQuery):
    data = call.data

    if data == "add_section":
        await call.message.answer("Yangi bo‘lim nomini yuboring:")
        await call.answer()

        # Next message handler will save the name
        @dp.message()
        async def receive_new_section(msg: types.Message):
            sec_name = msg.text.strip()
            if sec_name in sections:
                await msg.answer("Bu bo‘lim allaqachon mavjud.")
            else:
                sections[sec_name] = {"categories": [], "admin_id": None}
                await msg.answer(f"Bo‘lim qo‘shildi: {sec_name}")

            # Remove this temporary listener
            dp.message_handlers.pop()
    
    elif data.startswith("del_section:"):
        sec = data.split(":")[1]
        if sec in sections:
            del sections[sec]
            await call.message.answer(f"Bo‘lim o‘chirildi: {sec}")
        else:
            await call.message.answer("Bunday bo‘lim topilmadi!")
        await call.answer()

    else:
        await call.answer("Nomaʼlum tugma!")


# ================= RUN POLLING =================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())