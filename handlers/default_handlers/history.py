from telegram import Update
from telegram.ext import ContextTypes
from database.data_base import get_user_queries
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging


async def bot_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    queries = get_user_queries(user_id)
    page_number = int(context.args[0]) if context.args else 1  # Текущая страница, по умолчанию 1
    items_per_page = 5  # Количество запросов на страницу

    if queries:
        total_pages = (len(queries) + items_per_page - 1) // items_per_page  # Всего страниц
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        page_queries = queries[start_index:end_index]

        # Формируем кнопки для запросов
        keyboard = [
            [InlineKeyboardButton(
                text=f"{query}",
                callback_data=f"repeat_query:{query.split(':')[-1].strip()[:21]}"
            )] for query in page_queries
        ]

        # Добавляем кнопки пагинации
        pagination_buttons = []
        if page_number > 1:
            pagination_buttons.append(InlineKeyboardButton(
                text="⬅️ Предыдущая страница",
                callback_data=f"history_page:{page_number - 1}"
            ))
        if page_number < total_pages:
            pagination_buttons.append(InlineKeyboardButton(
                text="➡️ Следующая страница",
                callback_data=f"history_page:{page_number + 1}"
            ))
        if pagination_buttons:
            keyboard.append(pagination_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("История запросов:", reply_markup=reply_markup)
    else:   
        await update.message.reply_text("Запросы не найдены.")


async def history_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Уведомляем Telegram, что запрос обработан

    # Извлекаем номер страницы из callback_data
    page = int(query.data.split(":")[1])
    logging.info(f"Переход на страницу: {page}")

    # Сохраняем текущую страницу в контекст пользователя
    context.user_data['current_page'] = page

    # Загружаем запросы для нужной страницы
    user_id = query.from_user.id
    queries = get_user_queries(user_id)

    if queries:
        # Определяем границы страницы
        per_page = 5
        start = (page - 1) * per_page
        end = start + per_page
        page_queries = queries[start:end]

        # Создаем кнопки
        keyboard = []
        for query_text in page_queries:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{query_text}",
                    callback_data=f"repeat_query:{query_text.split(':')[-1].strip()[:21]}"
                )
            ])

        # Добавляем кнопку для перехода на следующую страницу, если есть еще элементы
        if end < len(queries):
            keyboard.append([
                InlineKeyboardButton(
                    text="➡️ Следующая страница",
                    callback_data=f"history_page:{page + 1}"
                )
            ])

        # Добавляем кнопку для перехода на предыдущую страницу, если это не первая
        if start > 0:
            keyboard.append([
                InlineKeyboardButton(
                    text="⬅️ Предыдущая страница",
                    callback_data=f"history_page:{page - 1}"
                )
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Проверяем, существует ли message перед вызовом edit_text
        if query.message:
            await query.message.edit_text("История запросов:", reply_markup=reply_markup)
        else:
            logging.info("query.message is None, невозможно обновить сообщение")
    else:
        if query.message:
            await query.message.edit_text("Запросы не найдены.")
        else:
            logging.info("query.message is None, невозможно обновить сообщение")

