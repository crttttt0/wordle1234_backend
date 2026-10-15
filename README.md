# wordle-one-two-three-four

REST API игры Wordle на FastAPI.

## Стек

- FastAPI + Gunicorn (UvicornWorker)
- PostgreSQL + SQLAlchemy (async) + Alembic
- uv для управления зависимостями
- Docker Compose + Traefik (reverse proxy, Let's Encrypt)

## Настройки

Конфигурация читается из `.env` (переменные с разделителем `__`), см.
`app/core/config.py`. Основные группы: `APP__*`, `JWT__*`, `DATABASE__*`,
`GAME__*`. Переменные `DOMAIN` и `ACME_EMAIL` приложение не читает — их
использует только Traefik.

`APP__CORS_ORIGINS` — список origin'ов веб-клиента (схема + хост + порт, без
слэша на конце). Для локальной разработки веба разрешены
`http://localhost:8080` и `http://127.0.0.1:8080`. Нативным мобильным клиентам
CORS не нужен.

## Локальный запуск

```bash
uv sync
uv run alembic upgrade head
just run-local
```

`just run-local` переопределяет `DATABASE__HOST` на `localhost` (в `.env`
указан `db` — хост внутри Docker-сети). Если локальные креды БД отличаются,
задай их в рецепте.

## Деплой

### Требования

- Linux-сервер с Docker и Docker Compose
- Домен, A-запись которого указывает на IP сервера
- Открытые порты 80 и 443 (порт приложения 8000 открывать не нужно)

### Шаги

1. Создать `.env` на сервере и заполнить:
   - `JWT__SECRET_KEY` — сгенерировать:
     `python -c "import secrets; print(secrets.token_hex(32))"`;
   - `DATABASE__PASSWORD` — пароль БД (можно любой, экранируется автоматически);
   - `ACME_EMAIL` — email для Let's Encrypt;
   - `APP__ALLOWED_HOSTS` — домен (+ `localhost` для healthcheck);
   - `APP__CORS_ORIGINS` — origin веб-клиента, если он будет на другом домене;
   - `DOMAIN` — домен.

2. Собрать и запустить:

   ```bash
   docker compose up -d --build
   ```

3. Проверить:

   ```bash
   docker compose ps
   curl https://<DOMAIN>/health
   ```

### Обновление

```bash
git pull
docker compose up -d --build
```

Миграции применяются автоматически при старте контейнера (`docker-entrypoint.sh`).

### Полезные команды (just)

```bash
just deploy     # собрать и поднять
just down       # остановить
just logs       # логи app
just migrate    # применить миграции вручную
```

## Архитектура

- `traefik` — принимает 80/443, редиректит на HTTPS, выпускает сертификаты Let's Encrypt.
- `app` — Gunicorn + UvicornWorker, 2 воркера, слушает 8000 только во внутренней сети.
- `db` — PostgreSQL, наружу не публикуется; креды берутся из `DATABASE__*`.
