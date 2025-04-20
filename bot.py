import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ключі
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Ініціалізація Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Flask app
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Хендлер для повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        gemini_response = model.generate_content(user_message)
        reply_text = gemini_response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        reply_text = "Вибач, сталася помилка при зверненні до Gemini."
    
    await update.message.reply_text(reply_text)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Ця частина була відсутня — вона ініціалізує application!
@app.before_first_request
def initialize_app():
    asyncio.get_event_loop().run_until_complete(application.initialize())

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
        return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running..."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)