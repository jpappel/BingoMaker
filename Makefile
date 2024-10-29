.PHONY: all lint lint-fix format test info

all: lint

lint:
	uvx ruff check

lint-fix:
	uvx ruff check --fix

format:
	uvx ruff format

test:
	uvx pytest

clean:
	uvx ruff clean

info:
	@echo "Targets"
	@echo "all      - lint the project"
	@echo "lint     - lint the project"
	@echo "lint-fix - lint and fix the project"
	@echo "format   - format the project"
	@echo "test     - run tests"
	@echo "clean    - clear caches for project tools"
