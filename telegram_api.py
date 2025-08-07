

from game_handler import GameHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramIO:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update = update
        self.context = context
        self.chat_id = update.effective_chat.id

    async def output(self, message: str):
        await self.update.message.reply_text(message)

    async def input(self, prompt: str = "") -> str:
        # In Telegram, input is handled through message handlers
        # This method is just for compatibility with the existing interface
        if prompt:
            await self.output(prompt)
        return ""


import asyncio


class AsyncIOWrapper:
    def __init__(self, async_io):
        self.async_io = async_io

    def output(self, message: str):
        # Запускаем асинхронный код из синхронного контекста
        asyncio.get_event_loop().run_until_complete(
            self.async_io.output(message)
        )

    def input(self, prompt: str = "") -> str:
        # Для ввода в Telegram нужно особое решение
        # Это упрощённый вариант - в реальности нужно сохранять future
        future = asyncio.Future()
        self.async_io.set_input_future(future)
        asyncio.get_event_loop().run_until_complete(
            self.async_io.output(prompt)
        )
        return asyncio.get_event_loop().run_until_complete(future)


class TelegramBot:
    def __init__(self):
        self.token = "8241702513:AAEqT5KKtMds_fxuj11qtH5f6-UuYTjL-Tg"
        self.application = Application.builder().token(self.token).build()

        # Add handlers
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                "MAIN": [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        self.application.add_handler(conv_handler)

        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Starts the conversation and asks for user info."""
        user = update.message.from_user
        logger.info("User %s started the conversation.", user.first_name)

        io = TelegramIO(update, context)
        username = user.username or str(user.id)
        handler = GameHandler(io, username)

        # Store handler in context
        context.user_data["handler"] = handler

        # Process initial state
        await handler.process(None)

        return "MAIN"

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Processes user messages."""
        user = update.message.from_user
        logger.info("Message from %s: %s", user.first_name, update.message.text)

        handler = context.user_data.get("handler")
        if not handler:
            await update.message.reply_text("Please start the bot with /start first.")
            return "MAIN"

        io = TelegramIO(update, context)
        handler.io = io  # Update IO for this message

        await handler.process(update.message.text)

        return "MAIN"

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)

        await update.message.reply_text(
            "Bye! You can start again with /start anytime.",
            reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Logs errors and sends a message to the user."""
        logger.error("Exception while handling an update:", exc_info=context.error)

        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                "An error occurred. Please try again or /start a new session."
            )

    def run(self):
        """Runs the bot until the user presses Ctrl-C"""
        self.application.run_polling()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()