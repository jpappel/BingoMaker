.PHONY: all lint lint-fix format test info server deploy lambdas

PYTHON_VERSION=3.13
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

server:
	uv run src/__init__.py

deploy/.terraform:
	@terraform -chdir=deploy init

remote-deploy: deploy/.terraform
	@terraform -chdir=deploy apply -auto-approve

remote-destroy: deploy/.terraform
	@terraform -chdir=deploy destroy -auto-approve

deploy:
	uv run --no-dev --directory=bingomaker gunicorn \
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

# Lambdas

lambdas: layer/layer.zip
	@uv run scripts/push_layer.py

layer:
	mkdir $@

layer/requirements.txt: pyproject.toml uv.lock | layer
	uv export --only-group lambda > $@

layer/python: layer/requirements.txt bingomaker
	uv pip install -r $< --target $@
	cp -r $(word 2, $^) layer/python

layer/layer.zip: layer/python
	@echo "---------------"
	@echo "Uncompressed layer size: $$(du -hd 0 layer/python)"
	@uv run scripts/lambda_zipper.py $@ layer/python
	@echo "Compressed layer size: $$(du -h layer/layer.zip)"

clean:
	uv run ruff clean
	rm -rf layer/*

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
		"remote-destroy - destroy application using terraform" \
		"lambdas   - build all lambda layers and functions"
