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
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/) *(отсутствует в requirements)*

## ⚙️ Установка и запуск

1. Клонируйте репозиторий:
    
    ```bash
    git clone https://github.com/EndiLobizon/kinopoisk-bot.git
    cd kinopoisk-bot

2. Установите зависимости:

    pip install -r requirements.txt

3. Создайте файл .env в корне проекта со следующим содержимым:
    
    BOT_TOKEN="your_telegram_bot_token"
    RAPID_API_KEY="your_rapidapi_key"

4. Запустите бота

    python main.py

## 💬 Разработка
Бот разрабатывается и тестируется локально на ПК.

## 👤 Автор
Евгений • @EndiLobizon


