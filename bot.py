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

# Отримуємо токен з оточення
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # наприклад: https://your-app.onrender.com/webhook

# Створюємо Telegram Application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Обробники команд ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Бот працює!")

# Додаємо обробники до application
application.add_handler(CommandHandler("start", start))

# === Одноразова ініціалізація ===
application_initialized = False

@app.before_request
def init_application_once():
    global application_initialized
    if not application_initialized:
        asyncio.get_event_loop().run_until_complete(application.initialize())
        application_initialized = True

# === Webhook ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

# === Кореневий маршрут для перевірки — необов’язково ===
@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is running!"

# === Запуск сервера ===
if __name__ == "__main__":
    # Встановлюємо webhook (тільки під час запуску)
    async def set_webhook():
        await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
        print("Webhook успішно налаштовано!")

    asyncio.get_event_loop().run_until_complete(set_webhook())

    # Flask слухає порт 10000 — Render шукає відкритий порт
    app.run(host="0.0.0.0", port=10000)