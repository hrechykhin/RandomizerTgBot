import os
import asyncio
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# Only load .env file locally
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    load_dotenv()

# === CONFIG ===
ANSWERS = [
    "✅ Yes, definitely!",
    "❌ No, not at all!",
]

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🚀 /start command triggered")
    keyboard = [[InlineKeyboardButton("🎲 Get an Answer", callback_data="get_answer")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Random Answer Bot! Choose an option below:",
        reply_markup=markup
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I received your message!")


# === CALLBACK HANDLER ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_answer":
        await context.bot.send_chat_action(
            chat_id=query.message.chat.id,
            action=ChatAction.TYPING
        )
        await asyncio.sleep(1)
        answer = random.choice(ANSWERS)
        new_text = f"🎉 Your answer is:\n\n{answer}"

        if query.message.text != new_text:
            await query.edit_message_text(new_text)
        else:
            # Forcefully add some variation if the same result is picked
            await query.edit_message_text(new_text + " 🎯")

        keyboard = [[InlineKeyboardButton("🔄 Ask Again", callback_data="get_answer")]]
        await query.message.reply_text(
            "Want to try again?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



def main():
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is missing in environment variables.")
        return

    # Create the Application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, echo))

    # Run the bot until Ctrl-C is pressed
    logger.info("Bot is running...")
    application.run_polling()


# === ENTRY POINT ===
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
