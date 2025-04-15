import requests
import logging
from config_data.config import RAPID_API_KEY
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database.data_base import check_possibility_of_saving, insert_movie


logger = logging.getLogger(__name__)


async def search_film_name(name_film: str, user_id: int, chat_id: int, bot, page_number: int = 1):
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page={page_number}&limit=1&query={name_film}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": RAPID_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Запрос к API: {url}")

        if response.status_code == 200:
            logger.info(f"Ответ от API: {response.status_code}")
            data = response.json()
            found_movies = False
            result = []  # Список для накопления результатов

            for movie in data["docs"]:

                movie_name = movie.get('name')
                if not movie_name:  # Если названия нет, ищем другой фильм
                    continue

                found_movies = True

                movie_year = movie.get('year')
                year_info = f'({movie_year})' if movie_year else ''

                rating_kp = movie.get("rating", {}).get("kp")
                rating_kp = float(rating_kp) if rating_kp else "Без оценки 🛑"

                rating_kp_display = (
                    round(rating_kp, 2) if isinstance(rating_kp, float) else rating_kp
                )

                description = movie.get('description')
                description_info = f'📝 Описание: {description}\n' if description\
                    else '📝 Описание где-то гуляет, не можем отыскать 😔\n'

                movie_length = movie.get('movieLength')
                length_info = f'⏱ Продолжительность: {movie_length} мин\n' if movie_length else ''

                age_rating = movie.get('ageRating')
                rating_info = f'🅰️ Возрастной рейтинг: {age_rating}+\n' if age_rating else ''

                # Извлекаем жанры
                genres = movie.get('genres', [])
                genre_info = f'🎭 Жанры: {", ".join([genre["name"] for genre in genres])}\n' \
                    if genres else '🎭 Жанры не указаны.\n'

                # Получаем URL фильма для кнопки
                movie_id = movie.get('id')
                insert_movie(movie_id, movie_name)
                movie_url = f"https://www.kinopoisk.ru/film/{movie_id}/"

                # Формируем информацию о фильме
                movie_info = (
                    f'🎬 {movie_name} {year_info}\n'
                    f'🌟 Рейтинг КиноПоиска: {rating_kp_display}\n'
                    f'{rating_info}'
                    f'{genre_info}'
                    f'{description_info}'
                    f'{length_info}'  # Добавляем строку с продолжительностью, если она есть
                )

                result.append(movie_info)

                if not check_possibility_of_saving(user_id, name_film, year_info.strip('()')):
                    save_button = [InlineKeyboardButton("Добавить в сохраненные",
                                                        callback_data=f"save_{movie_id}_{year_info.strip('()')}"
                                                                      f"_{page_number}")]
                else:
                    save_button = []

                # Кнопка для перехода на страницу фильма
                keyboard = [
                    [InlineKeyboardButton("Перейти на КиноПоиск", url=movie_url)],
                    [InlineKeyboardButton("Показать похожий фильм",
                                          callback_data=f"more_n_{page_number + 1}_{movie_id}")],
                    save_button
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                caption = '\n'.join(result)[:1024]

                poster = movie.get('poster')
                if poster and 'url' in poster and poster['url']:  # Проверяем, есть ли ключ 'url' в 'poster'
                    poster_url = poster['url']
                    logger.info(f"Постер найден для фильма: {movie_name}, URL: {poster_url}")

                    # Отправляем сообщение с изображением
                    await bot.send_photo(
                        chat_id,
                        poster_url,
                        caption=caption,
                        reply_markup=reply_markup
                    )
                    result.append(poster_url)

                else:
                    logger.info(f"Постер отсутствует для фильма: {movie_name}")
                    # Если постера нет, отправляем только текст
                    await bot.send_message(
                        chat_id,
                        text=f"Здесь должен быть постер, но он пропал без вести 😢\n\n{caption}",
                        reply_markup=reply_markup
                    )

                result = []

            if not found_movies:
                await bot.send_message(chat_id,
                                       f"К сожалению, по запросу '{name_film}' фильмов с названиями не найдено.")

        else:
            logger.error(f"Ошибка при запросе к API. Статус код: {response.status_code}, Ответ: {response.text}")
            return f"Ошибка {response.status_code}: {response.text}"

    except Exception as e:
        logger.exception(f"Произошла ошибка при выполнении запроса: {str(e)}")
        return f"Произошла ошибка при выполнении запроса: {str(e)}"


async def search_film_rating(rating: str, user_id: int, chat_id: int, bot, page_number: int = 1):

    url = f"https://api.kinopoisk.dev/v1.4/movie?page={page_number}&limit=5&selectFields=&rating.kp={rating}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": RAPID_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Запрос к API: {url}")

        if response.status_code == 200:
            logger.info(f"Ответ от API: {response.status_code}")
            data = response.json()
            found_movies = False
            result = []  # Список для накопления результатов
            for movie in data["docs"]:

                movie_name = movie.get('name')
                if not movie_name:
                    continue

                found_movies = True

                movie_year = movie.get('year')
                year_info = f'({movie_year})' if movie_year else ''

                rating_kp = movie.get("rating", {}).get("kp")
                rating_kp = float(rating_kp) if rating_kp else "Без оценки 🛑"

                rating_kp_display = (
                    round(rating_kp, 2) if isinstance(rating_kp, float) else rating_kp
                )

                description = movie.get('description')
                description_info = f'📝 Описание: {description}\n' if description \
                    else '📝 Описание где-то гуляет, не можем отыскать 😔\n'

                movie_length = movie.get('movieLength')
                length_info = f'⏱ Продолжительность: {movie_length} мин\n' if movie_length else ''

                age_rating = movie.get('ageRating')
                rating_info = f'🅰️ Возрастной рейтинг: {age_rating}+\n' if age_rating else ''

                # Извлекаем жанры
                genres = movie.get('genres', [])
                genre_info = f'🎭 Жанры: {", ".join([genre["name"] for genre in genres])}\n' \
                    if genres else '🎭 Жанры не указаны.\n'

                # Получаем URL фильма для кнопки
                movie_id = movie.get('id')
                insert_movie(movie_id, movie_name)
                movie_url = f"https://www.kinopoisk.ru/film/{movie_id}/"

                # Формируем информацию о фильме
                movie_info = (
                    f'🎬 {movie_name} {year_info}\n'
                    f'🌟 Рейтинг КиноПоиска: {rating_kp_display}\n'
                    f'{rating_info}'
                    f'{genre_info}'
                    f'{description_info}'
                    f'{length_info}'
                )

                result.append(movie_info)

                if not check_possibility_of_saving(user_id, movie_name, year_info.strip('()')):
                    save_button = [InlineKeyboardButton("Добавить в сохраненные",
                                                        callback_data=f"save_{movie_id}_{year_info.strip('()')}"
                                                                      f"_{page_number}")]
                else:
                    save_button = []

                # Кнопка для перехода на страницу фильма
                keyboard = [
                    [InlineKeyboardButton("Перейти на КиноПоиск", url=movie_url)],
                    [InlineKeyboardButton("Показать похожий фильм",
                                          callback_data=f"more_n_{page_number + 1}_{movie_id}")],
                    save_button
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                caption = '\n'.join(result)[:1024]

                poster = movie.get('poster')
                if poster and 'url' in poster and poster['url']:  # Проверяем, есть ли ключ 'url' в 'poster'
                    poster_url = poster['url']
                    logger.info(f'Постер найден для фильма: {movie_name}, URL: {poster_url}')
                    # Отправляем сообщение с изображением
                    await bot.send_photo(
                        chat_id,
                        poster_url,
                        caption=caption,
                        reply_markup=reply_markup
                    )

                else:
                    logger.info(f'Постер отсутствует для фильма: {movie_name}')
                    # Если постера нет, отправляем только текст
                    await bot.send_message(
                        chat_id,
                        text=f'Здесь должен быть постер, но он пропал без вести 😢\n\n{caption}',
                        reply_markup=reply_markup
                    )

                result = []

            if not found_movies:
                await bot.send_message(chat_id,
                                       f"К сожалению, по рейтингу '{rating}' фильмов с названиями не найдено.")

        else:
            logger.error(f"Ошибка при запросе к API. Статус код: {response.status_code}, Ответ: {response.text}")
            return f"Ошибка {response.status_code}: {response.text}"

    except Exception as e:
        logger.exception(f"Произошла ошибка при выполнении запроса: {str(e)}")
        return f"Произошла ошибка при выполнении запроса: {str(e)}"


async def search_film_genres(genre_name: str, user_id: int, chat_id: int, bot, page_number: int = 1):

    url = (f"https://api.kinopoisk.dev/v1.4/movie?page={page_number}"
           f"&limit=5&selectFields=&genres.name={genre_name.lower()}")

    headers = {
        "accept": "application/json",
        "X-API-KEY": RAPID_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Запрос к API: {url}")

        if response.status_code == 200:
            logger.info(f"Ответ от API: {response.status_code}")
            data = response.json()

            if not data.get('docs'):
                await bot.send_message(
                    chat_id,
                    f"К сожалению, по запросу '{genre_name}' фильмов не найдено. Попробуйте указать другой жанр."
                )
                return

            found_movies = False
            logger.info(f"Количество найденных фильмов: {len(data['docs'])}")
            result = []  # Список для накопления результатов
            for movie in data["docs"]:

                movie_name = movie.get('name')
                if not movie_name:
                    logger.info(f"Фильм без названия: {movie}")
                    continue

                found_movies = True

                movie_year = movie.get('year')
                year_info = f'({movie_year})' if movie_year else ''

                rating_kp = movie.get("rating", {}).get("kp")
                rating_kp = float(rating_kp) if rating_kp else "Без оценки 🛑"

                rating_kp_display = (
                    round(rating_kp, 2) if isinstance(rating_kp, float) else rating_kp
                )

                description = movie.get('description')
                description_info = f'📝 Описание: {description}\n' if description \
                    else '📝 Описание где-то гуляет, не можем отыскать 😔\n'

                movie_length = movie.get('movieLength')
                length_info = f'⏱ Продолжительность: {movie_length} мин\n' if movie_length else ''

                age_rating = movie.get('ageRating')
                rating_info = f'🅰️ Возрастной рейтинг: {age_rating}+\n' if age_rating else ''

                # Извлекаем жанры
                genres = movie.get('genres', [])
                genre_info = f'🎭 Жанры: {", ".join([genre["name"] for genre in genres])}\n' \
                    if genres else '🎭 Жанры не указаны.\n'

                # Получаем URL фильма для кнопки
                movie_id = movie.get('id')
                insert_movie(movie_id, movie_name)
                movie_url = f"https://www.kinopoisk.ru/film/{movie_id}/"

                # Формируем информацию о фильме
                movie_info = (
                    f'🎬 {movie_name} {year_info}\n'
                    f'🌟 Рейтинг КиноПоиска: {rating_kp_display}\n'
                    f'{rating_info}'
                    f'{genre_info}'
                    f'{description_info}'
                    f'{length_info}'
                )

                result.append(movie_info)

                if not check_possibility_of_saving(user_id, movie_name, year_info.strip('()')):
                    save_button = [InlineKeyboardButton("Добавить в сохраненные",
                                                        callback_data=f"save_{movie_id}_{year_info.strip('()')}"
                                                                      f"_{page_number}")]
                else:
                    save_button = []

                # Кнопка для перехода на страницу фильма
                keyboard = [
                    [InlineKeyboardButton("Перейти на КиноПоиск", url=movie_url)],
                    [InlineKeyboardButton("Показать похожий фильм",
                                          callback_data=f"more_n_{page_number + 1}_{movie_id}")],
                    save_button
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                caption = '\n'.join(result)[:1024]

                poster = movie.get('poster')
                if poster and 'url' in poster and poster['url']:  # Проверяем, есть ли ключ 'url' в 'poster'
                    poster_url = poster['url']
                    logger.info(f"Постер найден для фильма: {movie_name}, URL: {poster_url}")
                    # Отправляем сообщение с изображением
                    await bot.send_photo(
                        chat_id,
                        poster_url,
                        caption=caption,
                        reply_markup=reply_markup
                    )

                else:
                    logger.info(f"Постер отсутствует для фильма: {movie_name}")
                    # Если постера нет, отправляем только текст
                    await bot.send_message(
                        chat_id,
                        text=f"Здесь должен быть постер, но он пропал без вести 😢\n\n{caption}",
                        reply_markup=reply_markup
                    )

                result = []

            if not found_movies:
                await bot.send_message(chat_id,
                                       f"К сожалению, по жанру '{genre_name}' фильмов с названиями не найдено.")

        else:
            logger.error(f"Ошибка при запросе к API. Статус код: {response.status_code}, Ответ: {response.text}")
            return f"Ошибка {response.status_code}: {response.text}"

    except Exception as e:
        logger.exception(f"Произошла ошибка при выполнении запроса: {str(e)}")
        return f"Произошла ошибка при выполнении запроса: {str(e)}"
