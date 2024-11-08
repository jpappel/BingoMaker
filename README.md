# BingoMaker

## Development

### Setup

Please install the following

* [uv](https://docs.astral.sh/uv/#getting-started) for project management

```bash
git clone https://github.com/cs399f24/BingoMaker
cd BingoMaker
uv sync
```

### Testing

To run tests for the project you can either run `uv run pytest` or activate the virtual environment and run `pytest`

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

A local development server can be started via `make deploy`

## Deployment

### Monolith

The monolith version of the application can be deployed to a Linux VPS such as AWS EC2 by using the `userdata.sh` script provided in `deploy/`.
The script assumes that the system the software is being installed on has access to curl and uses the `yum` package manager. 
