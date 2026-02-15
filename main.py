import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database import init_db, get_connection


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    conn = get_connection()
    cursor = conn.cursor()

    # user bazada bormi tekshiramiz
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user.id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute("""
            INSERT INTO users (telegram_id, full_name, username, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            user.id,
            user.full_name,
            user.username,
            str(update.message.date)
        ))
        conn.commit()

    conn.close()

    await update.message.reply_text(
        "Xush kelibsiz!\nBo‘limni tanlang:"
    )


def main():
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
