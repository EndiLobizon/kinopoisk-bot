from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes


MAIN_MENU_KEYBOARD = [
    ['🔍 Поиск фильма/cериала по названию 🎬'],
    ['🔍 Поиск фильма/сериала по рейтингу 🌟'],
    ['🔍 Поиск фильма/cериала по жанру 🎭']
]


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)

    if update.message:
        await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    else:
        pass

