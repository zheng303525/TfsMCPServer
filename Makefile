.PHONY: help install install-dev test test-cov lint format type-check clean build run

# Default target
help:
	@echo "TFS MCP Server Development Commands"
	@echo "=================================="
	@echo "install       - Install production dependencies"
	@echo "install-dev   - Install development dependencies"
	@echo "test          - Run tests"
	@echo "test-cov      - Run tests with coverage report"
	@echo "lint          - Run linting checks"
	@echo "format        - Format code with black and isort"
	@echo "type-check    - Run mypy type checking"
	@echo "pre-commit    - Run all pre-commit hooks"
	@echo "clean         - Clean up build artifacts"
	@echo "build         - Build distribution packages"
	@echo "run           - Run the server locally"
	@echo "help          - Show this help message"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

# Testing targets
test:
	pytest

test-cov:
	pytest --cov=tfs_mcp_server --cov-report=html --cov-report=term-missing

# Code quality targets
lint:
	flake8 tfs_mcp_server/ tests/

format:
	black tfs_mcp_server/ tests/
	isort tfs_mcp_server/ tests/

type-check:
	mypy tfs_mcp_server/

pre-commit:
	pre-commit run --all-files

# Maintenance targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Development targets
run:
	python -m tfs_mcp_server.main

run-example:
	python example.py

# CI/CD targets
ci: install-dev lint type-check test

# Docker targets (if needed in the future)
docker-build:
	docker build -t tfs-mcp-server .

docker-run:
	docker run -it --rm tfs-mcp-server 