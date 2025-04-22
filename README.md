# КиноПоиск🍿 — Telegram-бот для поиска фильмов

**КиноПоиск🍿** — Telegram-бот на Python, который помогает находить фильмы по различным параметрам.  
Бот умеет искать фильмы по названию, рейтингу и жанру, сохранять избранное и вести историю запросов пользователя.

## 🔧 Возможности

- Поиск фильмов:
  - по названию
  - по рейтингу
  - по жанру
- Сохранение понравившихся фильмов
- Просмотр истории запросов
- Работа с inline-клавиатурами

## 📦 Команды

| Команда         | Описание                        |
|----------------|----------------------------------|
| `/start`        | Приветствие                     |
| `/help`         | Подсказка по использованию      |
| `/history`      | История запросов пользователя   |
| `/saved_movies` | Список сохранённых фильмов      |

## 🛠️ Технологии

- Python 3.x
- [requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [peewee](http://docs.peewee-orm.com/)
- [PyMySQL](https://pypi.org/project/PyMySQL/)
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/)

## 🌐 Используемые API

Бот использует публичный API от Kinopoisk.dev для получения информации о фильмах.

📌 Основные эндпоинты:
    🔍 Поиск по названию: 
    GET https://api.kinopoisk.dev/v1.4/movie/search?page={page}&limit=1&query={name}
    ⭐ Поиск по рейтингу: 
    GET https://api.kinopoisk.dev/v1.4/movie?page={page}&limit=5&selectFields=&rating.kp={rating}
    🎬 Поиск по жанру: 
    GET https://api.kinopoisk.dev/v1.4/movie?page={page}&limit=5&selectFields=&genres.name={genre}

⚠️ Для работы требуется API-ключ, который можно получить после регистрации на kinopoisk.dev.

🧾 Пример структуры ответа (JSON) по запросу "Интерстеллар":
{
  "docs": [
    {
      "id": 258687,
      "name": "Интерстеллар",
      "alternativeName": "Interstellar",
      "year": 2014,
      "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному...",
      "movieLength": 169,
      "rating": {
        "kp": 8.655,
        "imdb": 8.7
      },
      "votes": {
        "kp": 1052499,
        "imdb": 2323393
      },
      "genres": [
        { "name": "фантастика" },
        { "name": "драма" },
        { "name": "приключения" }
      ],
      "countries": [
        { "name": "США" },
        { "name": "Великобритания" },
        { "name": "Канада" }
      ],
      "poster": {
        "url": "https://image.openmoviedb.com/kinopoisk-images/.../orig"
      }
    }
  ]
}

## ⚙️ Установка и запуск

1. Клонируйте репозиторий:
    
    ```bash
    git clone https://github.com/EndiLobizon/kinopoisk-bot.git
    cd kinopoisk-bot

2. Установите зависимости:

    pip install -r requirements.txt

3. Создайте файл .env в корне проекта с содержимым из файла .env.template:
    
    BOT_TOKEN="your_telegram_bot_token"
    RAPID_API_KEY="your_rapidapi_key"

4. Запустите бота

    python main.py

## 💬 Разработка
Бот разрабатывается и тестируется локально на ПК.

## 👤 Автор
Евгений • @EndiLobizon


