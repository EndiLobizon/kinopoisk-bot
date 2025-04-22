import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

DEFAULT_COMMANDS = (
    ("start", "Запускает бота"),
    ("help", "Выводит справку"),
    ('history', 'Выводит историю запросов'),
    ('saves', 'Выводит сохраненные фильмы')
)


BASE_URL = "https://api.kinopoisk.dev/v1.4/movie"


def url_name(name_film: str, page_number: int = 1) -> str:
    return f"{BASE_URL}/search?page={page_number}&limit=1&query={name_film}"


def url_rating(rating: str, page_number: int = 1) -> str:
    return f"{BASE_URL}?page={page_number}&limit=5&selectFields=&rating.kp={rating}"


def url_genre(genre_name: str, page_number: int = 1) -> str:
    return f"{BASE_URL}?page={page_number}&limit=5&selectFields=&genres.name={genre_name.lower()}"

