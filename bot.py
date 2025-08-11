import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7228659347:AAHSUh-TfRKm8192IS5wS9RDhVxqPTT_3_g"

# اتصال به دیتابیس SQLite
conn = sqlite3.connect('bot_db.sqlite', check_same_thread=False)
cursor = conn.cursor()

# ایجاد جدول کاربران اگر وجود نداشته باشد
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 10
)
''')
conn.commit()

# استیت‌ها برای ConversationHandler
CHOOSING, CHATTING = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users(user_id, coins) VALUES (?, ?)", (user_id, 10))
        conn.commit()
    keyboard = [
        [InlineKeyboardButton("🔎 جستجوی هم‌صحبت", callback_data='find')],
        [InlineKeyboardButton("💰 خرید سکه", callback_data='buy')],
        [InlineKeyboardButton("🎁 دریافت سکه رایگان", callback_data='free')],
        [InlineKeyboardButton("👤 پروفایل من", callback_data='profile')],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! به ربات چت ناشناس خوش آمدی.", reply_markup=reply_markup)
    return CHOOSING

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'profile':
        cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
        coins = cursor.fetchone()[0]
        await query.edit_message_text(f"👤 پروفایل شما:\n💰 تعداد سکه‌ها: {coins}")

    elif query.data == 'help':
        text = ("راهنما:\n"
                "🔎 برای پیدا کردن هم‌صحبت روی «جستجوی هم‌صحبت» بزنید.\n"
                "💰 برای خرید سکه، گزینه «خرید سکه» را انتخاب کنید.\n"
                "🎁 برای دریافت سکه رایگان، «دریافت سکه رایگان» را بزنید.\n"
                "👤 برای دیدن پروفایل خود، «پروفایل من» را انتخاب کنید.")
        await query.edit_message_text(text)

    elif query.data == 'find':
        # چت کردن پیاده سازی نشده هنوز
        await query.edit_message_text("⚠️ قابلیت جستجوی هم‌صحبت هنوز فعال نشده. کمی صبر کن!")

    elif query.data == 'buy':
        await query.edit_message_text("💰 برای خرید سکه هنوز درگاه فعال نشده.")

    elif query.data == 'free':
        await query.edit_message_text("🎁 دریافت سکه رایگان هنوز فعال نشده.")

    return CHOOSING

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور شناخته نشده، لطفا از منوی اصلی استفاده کنید.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(button_handler)
            ],
            CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, unknown)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)

    print("ربات در حال اجراست...")
    application.run_polling()
