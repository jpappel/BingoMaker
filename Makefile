.PHONY: all lint lint-fix format test info server deploy

DEPLOY_NAME := BingoMaker
DEPLOY_WORKERS := 3
DEPLOY_BIND := 0.0.0.0:8080

all: lint

lint:
	uvx ruff check

lint-fix:
	uvx ruff check --fix

format:
	uvx ruff format

server:
	uv run --directory=src __init__.py

deploy:
	uv run --no-dev --directory=src gunicorn \
	--daemon --bind $(DEPLOY_BIND) \
	--workers $(DEPLOY_WORKERS) \
	--log-syslog \
	-p /tmp/BingoMaker.pid -n $(DEPLOY_NAME) \
	"app:create_app()"

test:
	uv run pytest

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
	@echo "server   - run a a development server"
	@echo "deploy   - deploy application usin gunicorn"
