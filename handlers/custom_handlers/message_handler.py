import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from api.api_kinopoisk import search_film_name, search_film_rating, search_film_genres
from database.data_base import save_user_query


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    bot = context.bot

    logging.info(f'Получено сообщение от пользователя {user_id}: {text}')

    user_state = context.user_data.get('state')

    if text == '🔍 Поиск фильма/cериала по названию 🎬':
        context.user_data['state'] = 'awaiting_film_name'
        await update.message.reply_text('Введите название фильма/сериала:')
    elif text == '🔍 Поиск фильма/сериала по рейтингу 🌟':
        context.user_data['state'] = 'awaiting_film_rating'
        await update.message.reply_text('Введите рейтинг в формате "Х.X-X.X". Пример: 7.2-8:')
    elif text == '🔍 Поиск фильма/cериала по жанру 🎭':
        context.user_data['state'] = 'awaiting_film_genres'
        await update.message.reply_text('Введите желаемый жанр фильма/сериала:')

    # Работа с состоянием
    elif user_state == 'awaiting_film_name':
        await search_film_name(text, user_id, chat_id, bot)
        save_user_query(user_id, text, 1)
        context.user_data['state'] = None  # Сброс состояния

    elif user_state == 'awaiting_film_rating':
        # Проверка на правильный формат ввода рейтинга
        rating_pattern = r'^\d+(\.\d+)?-\d+(\.\d+)?$'

        try:
            if re.match(rating_pattern, text):
                # Разделяем строку на два числа (минимальный и максимальный рейтинг)
                min_rating, max_rating = map(float, text.split('-'))

                # Проверяем, что оба значения находятся в пределах от 0 до 10
                if 0 <= min_rating <= 10 and 0 <= max_rating <= 10 and min_rating <= max_rating:
                    await search_film_rating(text, user_id, chat_id, bot)
                    save_user_query(user_id, text, 2)
                    context.user_data['state'] = None  # Сброс состояния
                else:
                    # Отправляем сообщение, что рейтинг выходит за допустимые пределы
                    await update.message.reply_text(
                        'Рейтинг должен быть в пределах от 0 до 10. Пожалуйста, введите корректный диапазон.')
                    # Не сбрасываем состояние, чтобы снова запросить ввод рейтинга
            else:
                # Если формат неверный, отправляем сообщение
                await update.message.reply_text(
                    'Неверный формат рейтинга. Пожалуйста, введите рейтинг в формате "X.X-X.X".')
                # Не сбрасываем состояние, чтобы снова запросить ввод рейтинга
        except ValueError:
            # Обрабатываем исключения при попытке преобразования строки в число
            await update.message.reply_text('Ошибка преобразования рейтинга. Пожалуйста, введите корректный диапазон.')
            # Не сбрасываем состояние, чтобы снова запросить ввод рейтинга

    elif user_state == 'awaiting_film_genres':
        await search_film_genres(text, user_id, chat_id, bot)
        save_user_query(user_id, text, 3)
        context.user_data['state'] = None  # Сброс состояния

    else:
        logging.warning(f'Неизвестная команда от пользователя {user_id}: {text}')
        await update.message.reply_text('Пожалуйста, используйте кнопки меню для взаимодействия.')


