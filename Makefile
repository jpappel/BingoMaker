.PHONY: all lint lint-fix format test info server deploy

DEPLOY_NAME := BingoMaker
DEPLOY_WORKERS := 3
DEPLOY_BIND := 0.0.0.0:80

all: lint test

lint:
	@uv run ruff check

lint-fix:
	uv run ruff check --fix

format:
	uv run ruff format
	terraform -chdir=deploy fmt

server:
	uv run src/__init__.py

deploy/.terraform:
	@terraform -chdir=deploy init

remote-deploy: deploy/.terraform
	@terraform -chdir=deploy apply -auto-approve

remote-destroy: deploy/.terraform
	@terraform -chdir=deploy destroy -auto-approve

deploy:
	uv run --no-dev --directory=src gunicorn \
	--daemon --bind $(DEPLOY_BIND) \
	--workers $(DEPLOY_WORKERS) \
	--log-syslog \
	-p /tmp/BingoMaker.pid -n $(DEPLOY_NAME) \
	"app:create_app()"

test:
	@uv run pytest -m "not localstack"

test-all:
	@docker compose up -d
	@uv run pytest
	@docker compose down

clean:
	uv run ruff clean

info:
	@printf "%s\n" \
		"Targets:" \
		"all      - lint the project and run some tests\n" \
		"lint     - lint the project" \
		"lint-fix - lint and fix the project" \
		"format   - format the project" \
		"test     - run tests which to not require localstack" \
		"test-all - run all tests, starting a localstack" \
		"clean    - clear caches for project tools" \
		"server   - run a a development server" \
		"deploy   - deploy application using gunicorn" \
		"remote-deploy - deploy application using terraform" \
		"remote-destroy - destroy application using terraform"
