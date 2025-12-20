.PHONY: help test test-unit test-integration test-e2e test-cov clean install run migrate

help: ## Показать это сообщение
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	poetry install

run: ## Запустить приложение
	poetry run uvicorn app.main:app --reload

migrate: ## Применить миграции
	poetry run alembic upgrade head

test: ## Запустить все тесты
	poetry run pytest -v

test-unit: ## Запустить только unit тесты
	poetry run pytest tests/unit/ -v

test-integration: ## Запустить только integration тесты
	poetry run pytest tests/integration/ -v

test-e2e: ## Запустить только e2e тесты
	poetry run pytest tests/e2e/ -v

test-cov: ## Запустить тесты с покрытием
	poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

test-watch: ## Запустить тесты в режиме watch (требует pytest-watch)
	poetry run ptw

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

docker-up: ## Запустить Docker контейнеры
	docker-compose up -d

docker-down: ## Остановить Docker контейнеры
	docker-compose down

docker-logs: ## Показать логи Docker
	docker-compose logs -f

lint: ## Проверить код (требует ruff)
	poetry run ruff check .

format: ## Отформатировать код (требует black)
	poetry run black .
