
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Ініціалізація Flask
app = Flask(__name__)

# Отримання токена і URL
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # https://your-app.onrender.com

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN або WEBHOOK_URL не встановлено")

# Telegram application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обробник команди
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Бот працює!")

application.add_handler(CommandHandler("start", start))

# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.get_event_loop().create_task(application.process_update(update))
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is running!"

# Запуск
if __name__ == "__main__":
    async def main():
        await application.initialize()
        await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        print("Webhook успішно налаштовано!")
        app.run(host="0.0.0.0", port=10000)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())