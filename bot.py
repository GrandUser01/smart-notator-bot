import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# === Ініціалізація Flask ===
app = Flask(__name__)

# === Змінні середовища ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # приклад: https://your-app.onrender.com

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не встановлено в змінних середовища")

# === Telegram Application ===
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Обробники команд ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Бот працює!")

application.add_handler(CommandHandler("start", start))

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))  # <-- найпростіший варіант
    return "ok"

# === Кореневий маршрут для перевірки ===
@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is running!"

# === Запуск Flask + встановлення webhook ===
if __name__ == "__main__":
    async def main():
        await application.initialize()
        await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        print("Webhook успішно налаштовано!")
        app.run(host="0.0.0.0", port=10000)

    asyncio.run(main())