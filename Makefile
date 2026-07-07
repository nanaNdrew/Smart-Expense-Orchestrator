.PHONY: build up down migrate upgrade test lint format

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose run --rm web alembic revision --autogenerate -m "$(m)"

upgrade:
	docker compose run --rm web alembic upgrade head

test:
	docker compose run --rm web pytest -v

lint:
	docker compose run --rm web ruff check .
	docker compose run --rm web mypy src

format:
	docker compose run --rm web ruff format .
