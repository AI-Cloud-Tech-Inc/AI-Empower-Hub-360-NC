.PHONY: help install test run clean lint format

help:
	@echo "AI Empower Hub 360 - Development Commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make test       Run tests"
	@echo "  make run        Run the application"
	@echo "  make clean      Clean up temporary files"
	@echo "  make lint       Run linters"
	@echo "  make format     Format code"

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest -v --cov=src

test-watch:
	pytest -v --cov=src --watch

run:
	python -m src.main

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

docker-build:
	docker build -t ai-empower-hub-360 .

docker-run:
	docker run -p 8000:8000 ai-empower-hub-360