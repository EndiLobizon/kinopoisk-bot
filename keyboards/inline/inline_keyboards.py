from api.api_kinopoisk import search_film_name, search_film_rating, search_film_genres
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.data_base import (get_search_id, save_user_film, check_possibility_of_saving, toggle_viewed_status,
                                get_movie_title_by_id)
from handlers.default_handlers.saved_movies import bot_saved_movies


async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    bot = context.bot
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message_id = query.message.message_id

    # Ответ на кнопки "Да" или "Нет"
    if data.startswith('more_n'):
        _, _, page_number, movie_id = data.split('_')
        movie_name = get_movie_title_by_id(movie_id)
        page_number = int(page_number)
        await search_film_name(movie_name, user_id, query.message.chat.id, bot, page_number)
        await query.answer()

    elif data.startswith('more_r'):
        _, _, page_number, movie_id = data.split('_')
        movie_name = get_movie_title_by_id(movie_id)
        page_number = int(page_number)
        await search_film_rating(movie_name, user_id, query.message.chat.id, bot, page_number)
        await query.answer()

    elif data.startswith('more_g'): #!!!!
        _, _, page_number, movie_id = data.split('_')
        movie_name = get_movie_title_by_id(movie_id)
        page_number = int(page_number)
        await search_film_genres(movie_name, user_id, query.message.chat.id, bot, page_number)
        await query.answer()

    elif data.startswith("save_"):
        _, movie_id, year_info, page_number = data.split('_')
        movie_name = get_movie_title_by_id(movie_id)
        page_number = int(page_number)
        # Проверяем возможность сохранения
        if not check_possibility_of_saving(user_id, movie_name, year_info):
            save_user_film(user_id, movie_id, movie_name, year_info)  # Сохраняем фильм в список пользователя
            # Обновляем клавиатуру без кнопки "Добавить в сохраненные"
            keyboard = [
                [InlineKeyboardButton("Перейти на КиноПоиск",
                                      url=f"https://www.kinopoisk.ru/film/{movie_name}/")],
                [InlineKeyboardButton("Показать похожий фильм",
                                      callback_data=f"more_n_{page_number + 1}_{movie_id}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Обновляем сообщение, удаляя кнопку "Добавить в сохраненные"
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup
            )
            # Уведомляем пользователя
            await query.answer("Фильм добавлен в сохраненные! ✅", show_alert=True)
        else:
            await query.answer("Этот фильм уже сохранен.", show_alert=True)

    elif query and query.data.startswith('repeat_query:'):
        user_request = query.data.split(':', 1)[1]
        search_id = get_search_id(user_id, user_request)
        if search_id == 1:
            await search_film_name(user_request, user_id, query.message.chat.id, bot)
        elif search_id == 2:
            await search_film_rating(user_request, user_id, query.message.chat.id, bot)
        elif search_id == 3:
            await search_film_genres(user_request, user_id, query.message.chat.id, bot)
        await query.answer()  # Закрыть уведомление Telegram

    elif data.startswith('view'):
        movie_data = data.split(':')[1]
        movie_id, movie_year = movie_data.split('_', 1)
        movie_name = get_movie_title_by_id(movie_id)
        year_of_release = movie_year.strip("()")
        toggle_viewed_status(user_id, movie_name, year_of_release)

        # Получаем текущую страницу из user_data
        page = context.user_data.get('current_page', 1)

        # Переходим обратно с сохранением текущей страницы
        await bot_saved_movies(update, context, page_number=page)

