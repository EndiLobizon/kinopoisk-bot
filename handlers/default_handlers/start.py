from telegram import Update
from telegram.ext import ContextTypes
from keyboards.reply import send_main_menu


async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.full_name
    user_id = update.effective_user.id
    await update.message.reply_text(f"Привет, {user_name}!\n Я чат-бот для поиска фильмов и сериалов 🎬🤖\n "
                                    f"Используйте кнопки для взаимодействия со мной!")
    await send_main_menu(update, context)

