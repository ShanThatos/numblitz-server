

cf:
	poetry run python -m src.base.cloudflared

start-dev:
	poetry run python -m src.main --dev

start-prod:
	poetry run python -m src.main --prod

migrate-dev:
	poetry run python -m src.database.migrate --dev

migrate-prod:
	poetry run python -m src.database.migrate --prod
