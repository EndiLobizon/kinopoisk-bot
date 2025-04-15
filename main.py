from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from config_data.config import BOT_TOKEN
from handlers.default_handlers import bot_start, bot_help, bot_history, bot_saved_movies
from handlers.custom_handlers import handle_message
from keyboards.inline.inline_keyboards import handle_button_click
from handlers.default_handlers.history import history_page_callback
from handlers.default_handlers.saved_movies import saves_page_callback
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()
    application.add_handler(CommandHandler("start", bot_start))
    application.add_handler(CommandHandler("help", bot_help))
    application.add_handler(CommandHandler("history", bot_history))
    application.add_handler(CommandHandler("saves", bot_saved_movies))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(history_page_callback, pattern=r"^history_page:\d+$"))
    application.add_handler(CallbackQueryHandler(saves_page_callback, pattern=r"^saves_page:\d+$"))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    application.run_polling()


if __name__ == '__main__':
    logging.info('Запуск бота...')
    main()


