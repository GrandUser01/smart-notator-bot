import os
import asyncio
from flask import Flask, request
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Зчитування токенів із середовища
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set!")

# Ініціалізація Telegram-бота та додатку
bot = Bot(BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = query_gemini(user_message)
    await update.message.reply_text(response)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запит до Gemini
def query_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        candidates = response.json().get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"]
        else:
            return "Не вдалося отримати відповідь від Gemini."
    else:
        return f"Помилка від Gemini: {response.status_code} - {response.text}"

# Flask додаток для вебхука
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return 'Bot is running!'

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        asyncio.run(application.process_update(update))
        return 'ok'
    return 'invalid', 400

# Встановлення Webhook
def set_webhook():
    WEBHOOK_URL = 'https://smart-notator-bot.onrender.com/webhook'
    webhook_url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}'
    response = requests.get(webhook_url)
    if response.status_code == 200:
        print("Webhook успішно налаштовано!")
    else:
        print(f"Помилка налаштування Webhook: {response.status_code} - {response.text}")

# Запуск Flask
if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)