.PHONY: up down logs migrate test build obs-up lint

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f

migrate:
	docker compose exec app alembic upgrade head

test:
	cd app && python -m pytest ../tests/ -v --tb=short

build:
	docker compose build --no-cache

obs-up:
	docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d

lint:
	cd app && ruff check . && bandit -r . -ll

shell-db:
	docker compose exec db psql -U finsight -d finsight
