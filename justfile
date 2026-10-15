set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

default:
    just --list

run:
    uv run uvicorn app.main:app --reload

run-local:
    $env:DATABASE__HOST = "localhost"; uv run uvicorn app.main:app --reload

format:
    uv run ruff format .
    uv run ruff check --select I --fix .

migrations-new message:
    uv run alembic revision -m "{{message}}" --autogenerate

migrations-up:
    uv run alembic upgrade head

migrations-down:
    uv run alembic downgrade -1

migrations-history:
    uv run alembic history

migrations-current:
    uv run alembic current

docker-build:
    docker compose build

deploy:
    docker compose up -d --build

down:
    docker compose down

logs:
    docker compose logs -f app

migrate:
    docker compose exec app alembic upgrade head
