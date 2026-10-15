# Wordle1234

Бэкенд для игры в Wordle на русском: нужно угадать слово из 5 букв за 6 попыток.
Учебный проект, сделан для мероприятия для первокурсников колледжа.

**Стек:** FastAPI · PostgreSQL · SQLAlchemy (async) · Alembic · JWT · uv · Docker Compose + Traefik

## Как устроена игра

1. Игрок регистрируется и входит, в ответ получает `access_token` и `refresh_token`.
2. `POST /api/games` начинает партию, сервер загадывает слово из словаря.
3. Клиент проверяет попытки сам и в конце отправляет результат в `POST /api/games/{id}/finish`.
4. За победу начисляются очки: чем меньше попыток, тем больше (от 600 до 100). За поражение 0.

| Метод | Путь | Что делает |
|---|---|---|
| POST | `/api/players/register` | Регистрация |
| POST | `/api/players/login` | Вход, выдаёт пару токенов |
| POST | `/api/players/refresh` | Новая пара токенов по refresh-токену |
| GET | `/api/players/me` | Текущий игрок 🔒 |
| GET | `/api/players/me/stats` | Статистика игрока 🔒 |
| GET | `/api/players/leaderboard` | Таблица лидеров |
| POST | `/api/games` | Начать партию 🔒 |
| GET | `/api/games/{id}` | Состояние партии 🔒 |
| POST | `/api/games/{id}/finish` | Завершить партию 🔒 |

🔒 нужен заголовок `Authorization: Bearer <access_token>`.

Интерактивная документация: <http://localhost:8000/docs>. Войти можно кнопкой **Authorize**.

## Настройка `.env`

Создай файл `.env` в корне проекта:

```env
# Приложение
APP__DEBUG=false
APP__ALLOWED_HOSTS=["localhost","127.0.0.1"]
APP__CORS_ORIGINS=["http://localhost:8080"]

# JWT
JWT__ALGORITHM=HS256
JWT__SECRET_KEY=change-me
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT__REFRESH_TOKEN_EXPIRE_DAYS=7

# База данных (для запуска через Docker: DATABASE__HOST=db)
DATABASE__USER=wordle_user
DATABASE__PASSWORD=wordle_password
DATABASE__HOST=localhost
DATABASE__PORT=5432
DATABASE__NAME=wordle_db
DATABASE__ECHO=false
DATABASE__POOL_SIZE=5
DATABASE__MAX_OVERFLOW=10

# Игра
GAME__MAX_ATTEMPTS=6
GAME__POINTS_PER_ATTEMPT=100
GAME__LEADERBOARD_SIZE=10

# Только для Docker-деплоя, их читает Traefik
DOMAIN=example.com
ACME_EMAIL=you@example.com
```

Секретный ключ для JWT можно сгенерировать так:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

`APP__CORS_ORIGINS` — адреса веб-клиента (схема, хост и порт, без `/` в конце). Мобильным клиентам CORS не нужен.

## Локальный запуск

Понадобятся Python 3.12+, [uv](https://docs.astral.sh/uv/) и PostgreSQL.
Если своего Postgres нет, его можно поднять в Docker:

```bash
docker run -d --name wordle-db -e POSTGRES_USER=wordle_user -e POSTGRES_PASSWORD=wordle_password -e POSTGRES_DB=wordle_db -p 5432:5432 postgres:18-alpine
```

Затем установи зависимости, примени миграции и запусти сервер:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Сервер будет доступен на <http://localhost:8000>, документация на <http://localhost:8000/docs>.
Если установлен [just](https://github.com/casey/just), те же шаги выполняют `just migrations-up` и `just run`.

## Запуск через Docker

`docker compose` поднимает три контейнера: PostgreSQL, приложение (Gunicorn, 2 воркера) и Traefik,
который выпускает HTTPS-сертификат Let's Encrypt. Понадобится сервер с Docker, домен, указывающий
на этот сервер, и открытые порты 80 и 443.

1. В `.env` укажи `DATABASE__HOST=db`, свои `DOMAIN` и `ACME_EMAIL`, а домен добавь в
   `APP__ALLOWED_HOSTS` (`localhost` оставь, он нужен для healthcheck).
2. Собери и запусти:

   ```bash
   docker compose up -d --build
   ```

3. Проверь, что всё поднялось:

   ```bash
   curl https://<DOMAIN>/health
   ```

Миграции применяются автоматически при старте контейнера. Обновление: `git pull`, затем снова `docker compose up -d --build`.

| Команда | Что делает |
|---|---|
| `just deploy` | Собрать и поднять |
| `just down` | Остановить |
| `just logs` | Логи приложения |
| `just migrate` | Применить миграции вручную |

## Структура

```
app/
├── api/endpoints/   # роуты: players, games
├── core/            # настройки, JWT, зависимости, исключения
├── database/        # подключение, сессия, миграции Alembic
├── models/          # SQLAlchemy-модели
├── repositories/    # запросы к БД
├── services/        # бизнес-логика
└── data/words_5.txt # словарь слов
```
