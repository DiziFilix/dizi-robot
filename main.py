import os
import asyncio
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN_FIRST")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # مثال: @YourChannel
HIDDEN_GROUP_ID = int(os.getenv("HIDDEN_GROUP_ID"))  # مثلاً: -1001234567890

# mapping بین episode_key و message_id
episode_files = {
    "got_s01e01": 101,
    "got_s01e02": 102,
    "breaking_bad_s01e01": 201,
    # بقیه قسمت‌ها رو اینجا اضافه کن
}

# موقت نگه‌داشتن درخواست کاربر
pending_users = {}

# 🚀 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if args:
        episode_key = args[0]
        if episode_key not in episode_files:
            await update.message.reply_text("❌ فایل مورد نظر پیدا نشد.")
            return

        pending_users[user_id] = episode_key
    else:
        await update.message.reply_text("❗ لطفاً از طریق لینک اختصاصی وارد شوید.")
        return

    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ عضو شدم", callback_data='check')]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 سلام رفیق!\nبرای دریافت قسمت سریال اول باید عضو کانال بشی 👇",
        reply_markup=markup
    )

# ✅ بررسی عضویت
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in pending_users:
        await query.edit_message_text("❗ خطا: ابتدا از طریق لینک وارد شوید.")
        return

    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if member.status in ['member', 'administrator', 'creator']:
        episode_key = pending_users.pop(user_id)
        message_id = episode_files.get(episode_key)

        if not message_id:
            await query.edit_message_text("❌ فایل مربوط به این قسمت پیدا نشد.")
            return

        await query.edit_message_text("✅ عضویتت تایید شد! در حال ارسال فایل...")

        sent = await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=HIDDEN_GROUP_ID,
            message_id=message_id
        )

        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ این فایل فقط ۳۵ ثانیه باقی می‌مونه، سریع ذخیره‌اش کن!",
        )

        await asyncio.sleep(35)
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=sent.message_id)
        except:
            pass
    else:
        await query.answer("🚫 هنوز عضو کانال نشدی!", show_alert=True)

# اجرای اصلی ربات
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(check_membership, pattern='^check$'))

    print("🤖 ربات آماده‌ست...")
    await app.run_polling()
