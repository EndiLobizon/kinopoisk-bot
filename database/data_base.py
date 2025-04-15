import logging
from typing import Any, List

from peewee import *
import pymysql


def ensure_database_exists():
    connection = pymysql.connect(host='localhost', user='root', password='456rty321ewqHD')
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS test_final;")
    connection.close()


def ensure_table_exists():
    ensure_database_exists()
    db.connect()
    db.create_tables([UserQuery, UserSaves, MoviesId], safe=True)


# Настройки подключения
db = MySQLDatabase('test_final', user='root', password='456rty321ewqHD', host='localhost')


class UserQuery(Model):
    user_id = IntegerField()
    query = TextField()
    search_id = IntegerField()
    timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db


class UserSaves(Model):
    user_id = IntegerField()
    movie_id = TextField()
    film_name = TextField()
    year_of_release = TextField()
    viewed_or_not = BooleanField(default=False)

    class Meta:
        database = db


class MoviesId(Model):
    movie_id = TextField()
    film_name = TextField()

    class Meta:
        database = db


# Убедимся, что база данных и таблицы существуют
ensure_table_exists()


def insert_movie(movie_id: str, film_name: str) -> None:
    # Попробуем создать запись в таблице, если такого movie_id нет
    try:
        movie, created = MoviesId.get_or_create(movie_id=movie_id, film_name=film_name)
        if created:
            logging.info(f"Фильм '{film_name}' с ID {movie_id} добавлен в базу данных.")
        else:
            logging.info(f"Фильм '{film_name}' с ID {movie_id} уже существует в базе данных.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении фильма: {e}")


def get_movie_title_by_id(movie_id: str) -> str | None:
    try:
        movie = MoviesId.get(MoviesId.movie_id == movie_id)
        return movie.film_name  # Возвращаем название фильма
    except DoesNotExist:
        return None  # Если фильм с таким ID не найден


def save_user_query(user_id: int, user_request: str, search_id: int) -> None:
    UserQuery.create(
        user_id=user_id,
        query=user_request,
        search_id=search_id
    )


def save_user_film(user_id: int, movie_id: int, film_name: str, year_of_release: str) -> None:
    UserSaves.create(
        user_id=user_id,
        movie_id=movie_id,
        film_name=film_name,
        year_of_release=year_of_release,
        viewed_or_not=False
    )


def check_possibility_of_saving(user_id: int, film_name: str, year_of_release: str) -> bool:
    # Проверяем, существует ли запись для данного пользователя и фильма
    exists = UserSaves.select().where(
        (UserSaves.user_id == user_id) &
        (UserSaves.film_name == film_name) &
        (UserSaves.year_of_release == year_of_release)
    ).exists()

    # Возвращаем True, если такая запись существует, иначе False
    return exists


def get_user_queries(user_id: int) -> list[str]:
    queries = (
        UserQuery
        .select()
        .where(UserQuery.user_id == user_id)
        .order_by(UserQuery.timestamp.desc())
    )
    # Формируем список строк для возврата
    return [f"{query.timestamp}: {query.query}" for query in queries]


def get_user_saves(user_id: int) -> list[str]:
    saves = (
        UserSaves
        .select()
        .where(UserSaves.user_id == user_id)
    )

    return [f"{save.film_name}_({save.year_of_release})_{save.viewed_or_not}_{save.movie_id}" for save in saves]


def toggle_viewed_status(user_id: int, film_name: str, year_of_release: str) -> None:
    film_name = film_name.strip()
    year_of_release = str(year_of_release)
    save = UserSaves.select().where(
        (UserSaves.user_id == user_id) &
        (UserSaves.film_name == film_name) &
        (UserSaves.year_of_release == year_of_release)
    ).first()

    if save:
        logging.info(f"Found record: {save.viewed_or_not}")
        save.viewed_or_not = not save.viewed_or_not
        save.save()
        logging.info(f"Updated record: {save.viewed_or_not}")

        # Проверим, что изменения действительно сохранились
        updated_save = UserSaves.get(
            UserSaves.user_id == user_id,
            UserSaves.film_name == film_name,
            UserSaves.year_of_release == year_of_release
        )
        logging.info(f"Record after save: {updated_save.viewed_or_not}")
    else:
        logging.info("No record found for the given parameters.")


def get_search_id(user_id: int, query: str) -> int | None:
    # Поиск в базе данных id запроса (название, рейтинг, жанр)
    search_id_query = (
        UserQuery
        .select(UserQuery.search_id)
        .where(
            (UserQuery.user_id == user_id) &
            ((UserQuery.query == query) | (UserQuery.query.startswith(query)))
            # Сравниваем либо полное название, либо начало
        )
        .limit(1)
    )

    # Проверяем, есть ли результат и возвращаем search_id
    if search_id_query.exists():
        return search_id_query[0].search_id  # Возвращаем найденный search_id
    else:
        return None  # Если не найдено соответствия


