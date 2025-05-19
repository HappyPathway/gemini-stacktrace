.PHONY: help test test-single lint format type-check all clean install

# Configuration
POETRY = poetry
PYTEST = $(POETRY) run pytest
PYTEST_ARGS = -v
RUFF = $(POETRY) run ruff
MYPY = $(POETRY) run mypy
PACKAGE = gemini_stacktrace

help:
	@echo "Available commands:"
	@echo " test           - Run tests with pytest"
	@echo " test-single    - Run a specific test file (usage: make test-single TEST_FILE=tests/test_file.py)"
	@echo " test-coverage  - Run tests with coverage report"
	@echo " lint           - Run linter (ruff)"
	@echo " lint-fix       - Run linter and try to fix issues automatically"
	@echo " format         - Format code with ruff"
	@echo " type-check     - Check types with mypy"
	@echo " all            - Run all checks (lint, type-check, test)"
	@echo " clean          - Clean up cache directories"
	@echo " install        - Install dependencies with Poetry"

test:
	$(PYTEST) $(PYTEST_ARGS) $(filter-out $@,$(MAKECMDGOALS))

test-single:
	$(PYTEST) $(PYTEST_ARGS) $(TEST_FILE)

test-coverage:
	$(PYTEST) $(PYTEST_ARGS) --cov=$(PACKAGE) --cov-report=term --cov-report=html $(filter-out $@,$(MAKECMDGOALS))

lint:
	$(RUFF) check $(PACKAGE) tests

lint-fix:
	$(RUFF) check --fix $(PACKAGE) tests

format:
	$(RUFF) format $(PACKAGE) tests

type-check:
	$(MYPY) $(PACKAGE)

all: lint format type-check test

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

install:
	$(POETRY) install

# Allow passing arguments to pytest (e.g., make test tests/test_agent.py)
%:
	@:
