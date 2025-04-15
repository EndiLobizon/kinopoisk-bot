import logging

from telegram import Update
from telegram.ext import ContextTypes
from database.data_base import get_user_saves
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def bot_saved_movies(update: Update, context: ContextTypes.DEFAULT_TYPE, page_number: int = 1) -> None:
    user_id = update.effective_user.id
    user_data_saves = get_user_saves(user_id)

    if context.args:
        page_number = int(context.args[0])
    else:
        page_number = context.user_data.get('current_page', 1)

    items_per_page = 3

    if user_data_saves:
        total_pages = (len(user_data_saves) + items_per_page - 1) // items_per_page  # Всего страниц
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        page_saves = user_data_saves[start_index:end_index]

        keyboard = []
        page_offset = (page_number - 1) * items_per_page

        for i, data_saves in enumerate(page_saves):
            try:
                film_data, view, movie_id = data_saves.rsplit('_', 2)
                movie_name, movie_year = film_data.rsplit('_', 1)
                button_text = (str(page_offset + i + 1) + ') ' + shorten_name(movie_name) + ' ' + movie_year +
                               (' ✅' if view == 'True' else ' ❌'))
                film_button = InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"view:{movie_id}_{movie_year}"  # передаем полное имя с годом
                )

                movie_url = f"https://www.kinopoisk.ru/film/{movie_id}/"
                link_button = InlineKeyboardButton(text='Перейти на КиноПоиск', url=movie_url)

                keyboard.append([film_button])  # первая строка — кнопка фильма
                keyboard.append([link_button])  # вторая строка — кнопка перехода

            except Exception as e:
                print(f"Ошибка при добавлении кнопки: {e}")
                continue

        # Добавляем кнопки пагинации
        pagination_buttons = []
        if page_number > 1:
            pagination_buttons.append(InlineKeyboardButton(
                text="⬅️ Предыдущая страница",
                callback_data=f"saves_page:{page_number - 1}"
            ))
        if page_number < total_pages:
            pagination_buttons.append(InlineKeyboardButton(
                text="➡️ Следующая страница",
                callback_data=f"saves_page:{page_number + 1}"
            ))
        if pagination_buttons:
            keyboard.append(pagination_buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text("Сохраненные фильмы:", reply_markup=reply_markup)
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.edit_message_text("Сохраненные фильмы:", reply_markup=reply_markup)
    else:
        if update.message:
            await update.message.reply_text("Фильмы не найдены.")
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.edit_message_text("Фильмы не найдены.")


async def saves_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Уведомляем Telegram, что запрос обработан

    page_number = int(query.data.split(":")[1])
    logging.info(f"Переход на страницу: {page_number}")

    # Сохраняем текущую страницу в контекст пользователя
    context.user_data['current_page'] = page_number

    # Загружаем запросы для нужной страницы
    user_id = query.from_user.id
    user_data_saves = get_user_saves(user_id)

    if user_data_saves:
        # Определяем границы страницы
        per_page = 3
        start = (page_number - 1) * per_page
        end = start + per_page
        page_saves = user_data_saves[start:end]

        keyboard = []
        page_offset = (page_number - 1) * per_page  # Смещение для правильной нумерации

        for i, data_saves in enumerate(page_saves):
            try:
                film_data, view, movie_id = data_saves.rsplit('_', 2)
                movie_name, movie_year = film_data.rsplit('_', 1)
                button_text = (str(page_offset + i + 1) + ') ' + shorten_name(movie_name) + ' ' + movie_year +
                               (' ✅' if view == 'True' else ' ❌'))
                film_button = InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"view:{movie_id}_{movie_year}"  # передаем полное имя с годом
                )

                movie_url = f"https://www.kinopoisk.ru/film/{movie_id}/"
                link_button = InlineKeyboardButton(text='Перейти на КиноПоиск', url=movie_url)

                keyboard.append([film_button])  # первая строка — кнопка фильма
                keyboard.append([link_button])  # вторая строка — кнопка перехода

            except Exception as e:
                print(f"Ошибка при добавлении кнопки: {e}")
                continue

        # Добавляем кнопку для перехода на следующую страницу, если есть еще элементы
        if end < len(user_data_saves):
            keyboard.append([
                InlineKeyboardButton(
                    text="➡️ Следующая страница",
                    callback_data=f"saves_page:{page_number + 1}"
                )
            ])

        # Добавляем кнопку для перехода на предыдущую страницу, если это не первая
        if start > 0:
            keyboard.append([
                InlineKeyboardButton(
                    text="⬅️ Предыдущая страница",
                    callback_data=f"saves_page:{page_number - 1}"
                )
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Проверяем, существует ли message перед вызовом edit_text
        if query.message:
            await query.message.edit_text("Сохраненные фильмы:", reply_markup=reply_markup)
        else:
            logging.info("query.message is None, невозможно обновить сообщение")
    else:
        if query.message:
            await query.message.edit_text("Фильмы не найдены.")
        else:
            logging.info("query.message is None, невозможно обновить сообщение")


def shorten_name(name):
    return name[:33] + "..." if len(name) > 33 else name
