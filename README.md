# BingoMaker

## Development

### Setup

Please ensure you have the following installed

* [uv](https://docs.astral.sh/uv/#getting-started) for project management
* [docker](https://www.docker.com/)

```bash
git clone https://github.com/cs399f24/BingoMaker
cd BingoMaker
uv sync
```

### Testing

To run tests for the project you can run `make test` for tests without a [LocalStack](https://www.localstack.cloud/) instance or use `make test-full` for all tests.

### Linting/Formatting

[Ruff](https://docs.astral.sh/ruff/) is used to lint and format the project.

Linting can be done in the following ways

```bash
make lint
uv run ruff check
.venv/bin/ruff check
```

Formatting can be done similarly

```bash
make format
uv run ruff format
.venv/bin/ruff format
```

### Development Server

A local development server which listens on `0.0.0.0:8080` can be started via `make server`

## Deployment

### Monolith

The monolith version of the application can be deployed to a Linux VPS such as AWS EC2 by using the `userdata.sh` script provided in `deploy/`.
The script assumes that the system the software is being installed on has access to curl and uses the `yum` package manager. 

## API

The API is fully documented according to the OpenAPI 3.0.3 spec in `api.yml`.
