.PHONY: help install install-dev test lint format clean build upload docs

help:
	@echo "Available commands:"
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package"
	@echo "  make upload       - Upload to PyPI"
	@echo "  make docs         - Generate documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --cov=api2pydantic --cov-report=term-missing --cov-report=html

test-verbose:
	pytest -v --cov=api2pydantic --cov-report=term-missing

lint:
	flake8 api2pydantic tests
	mypy api2pydantic --ignore-missing-imports

format:
	black api2pydantic tests
	isort api2pydantic tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

upload-test: build
	twine upload --repository testpypi dist/*

docs:
	@echo "Documentation generation not yet implemented"

# Run the example
example:
	python -m api2pydantic examples/sample_response.json

# Quick start for new contributors
setup: install-dev
	@echo "✓ Development environment ready!"
	@echo "Run 'make test' to verify everything works"