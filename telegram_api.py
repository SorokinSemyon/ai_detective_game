

from game_handler import GameHandler
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import logging
from auth import TELEGRAM_TOKEN

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


class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        # Увеличиваем количество worker'ов (по умолчанию 1)
        self.application = Application.builder().token(self.token).build()

        # Используем более простой обработчик вместо ConversationHandler,
        # если сложная логика не требуется
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("cancel", self.cancel))

        # Оптимизированный обработчик ошибок
        self.application.add_error_handler(self.error_handler)

        # Предзагрузка данных при инициализации
        self.user_handlers = {}  # Кэш обработчиков пользователей

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