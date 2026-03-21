.PHONY: help install test run clean lint format \
        docker-build docker-run docker-up docker-down docker-logs docker-shell docker-ps

help:
	@echo ""
	@echo "  AI Empower Hub 360 - Development Commands"
	@echo "  =========================================="
	@echo ""
	@echo "  LOCAL DEV"
	@echo "  make install       Install Python dependencies"
	@echo "  make run           Run app locally (port 8003)"
	@echo "  make test          Run tests with coverage"
	@echo "  make lint          Run linters"
	@echo "  make format        Format code"
	@echo "  make clean         Clean temp files"
	@echo ""
	@echo "  DOCKER"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start all services (app + redis)"
	@echo "  make docker-down   Stop all services"
	@echo "  make docker-logs   Tail container logs"
	@echo "  make docker-ps     List running containers"
	@echo "  make docker-shell  Open shell inside app container"
	@echo ""

# ── Local Dev ──────────────────────────────────────────────
install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload

test:
	pytest -v --cov=src

test-watch:
	pytest -v --cov=src --watch

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check src/ tests/ --fix

# ── Docker ─────────────────────────────────────────────────
docker-build:
	docker build -t ai-empower-hub-360:latest .

docker-run:
	docker run --env-file .env -p 8003:8003 ai-empower-hub-360:latest

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f app

docker-ps:
	docker compose ps

docker-shell:
	docker compose exec app /bin/bash