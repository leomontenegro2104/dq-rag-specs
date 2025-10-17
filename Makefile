.PHONY: install test lint format clean run-etl run-api

# Install dependencies
install:
	pip install -e .

# Run tests
test:
	pytest tests/ -v

# Lint code
lint:
	ruff check src/ tests/
	mypy src/

# Format code
format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

# Clean cache and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Run ETL pipeline
run-etl:
	python -m src.etl.run

# Run RAG API
run-api:
	uvicorn src.rag.api:app --reload

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files