from telegram import Update
from telegram.ext import ContextTypes
from config_data.config import DEFAULT_COMMANDS


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    await update.message.reply_text("\n".join(text))

