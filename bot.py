import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests
import signal
import sys
from flask import Flask, request

# Зчитуємо токени з середовища
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set!")

# Функція, яка надсилає запит до Gemini
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

# Обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = query_gemini(user_message)
    await update.message.reply_text(response)

# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Використовуємо run_polling() замість run()
    app.run_polling()

    # Flask додаток для запуску на Render (відкриває порт)
    flask_app = Flask(__name__)

    @flask_app.route('/')
    def index():
        return 'Bot is running...'

    # Оновлений webhook
    @flask_app.route('/webhook', methods=['POST'])
    def webhook():
        # Отримуємо дані у форматі JSON
        json_data = request.get_json()

        # Перевіряємо, чи отримано правильні дані
        if json_data:
            update = Update.de_json(json_data, app.bot)
            app.process_new_updates([update])
            return 'ok'
        else:
            return 'Invalid data received', 400

    # Слухати порт
    port = os.environ.get("PORT", 8080)  # Render відкриває порт 8080 за замовчуванням
    flask_app.run(host='0.0.0.0', port=port)

# Налаштування Webhook для Telegram
WEBHOOK_URL = 'https://smart-notator-bot.onrender.com'  # Замініть на URL вашого додатку в Render

# Налаштуємо Webhook для Telegram
def set_webhook():
    webhook_url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}'
    response = requests.get(webhook_url)
    if response.status_code == 200:
        print("Webhook успішно налаштовано!")
    else:
        print(f"Помилка налаштування Webhook: {response.status_code} - {response.text}")

# Викликаємо функцію для налаштування Webhook
set_webhook()