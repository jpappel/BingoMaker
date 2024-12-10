# BingoMaker

![Website Demo](Demo.mp4)

## Notes

### Lambdacism

* build layer for each module

## Development

### Setup

Please ensure you have the following installed

* [uv](https://docs.astral.sh/uv/#getting-started) for project management
* [docker](https://www.docker.com/)
* [terraform](https://developer.hashicorp.com/terraform/install)


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

Deployment is done via Terraform. the `deploy` directory contains the necessary terraform files to deploy the application

### Deploy
running `make remote-deploy` will create all the necessary resources in AWS.

After the resources are created, the application will need to be deployed on [AWS Amplify](https://us-east-1.console.aws.amazon.com/amplify/apps).

This is due to a limitation in Terraform where it cannot deploy a Amplify App without a backend. [#24720](https://github.com/hashicorp/terraform-provider-aws/issues/24720)

### Destroy
to destroy the resources run `make remote-destroy`.


## API

The API is fully documented according to the OpenAPI 3.0.3 spec in `api.yml`.
