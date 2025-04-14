from telegram.ext import ApplicationBuilder

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('support', support))
    app.add_handler(CallbackQueryHandler(check_membership, pattern='^check$'))
    app.add_handler(CallbackQueryHandler(handle_support_buttons, pattern='^(advertise|report)$'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_messages))

    print("🤖 ربات فعال شد...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())  # برای اجرا در محیط‌های معمولی
    except RuntimeError as e:
        if str(e).startswith("This event loop is already running"):  # در صورتی که لوپ در حال اجراست
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise
