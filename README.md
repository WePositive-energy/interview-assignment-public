# WePositive FastAPI Microservice Template
Template repository for We+ FastAPI microservices

## Installation
* `poetry install`
* `poetry run pre-commit install`
* copy and adjust `.env.example` into `.env`

## Running tests
* `poetry run pytest`
* Running tests, linting and type checking on all files: `poetry run pre-commit run --all-files`

## Making migrations
* `poetry run alembic revision --autogenerate -m "<my description>"`

## Running locally
* `poetry run serve dev|prod`
The [serve command](fastapi_microservice/management/serve.py) takes the following environment variables
to change how it runs with [uvicorn](https://www.uvicorn.org/settings/#http):
* FASTAPI_PORT (default 8000)
* FASTAPI_HOST (default 127.0.0.1)
* FASTAPI_ROOT_PATH (default None, so it serves on `/`)
* FASTAPI_PROXY_HEADERS (default False)
* FASTAPI_FORWARDED_ALLOW_IPS (default None, so not set)

## Running in docker
* make a `.env.docker` file to put in the container with required config parameters, or use the -e switch to `docker run`.
  Make sure not to publish sensitive data in there and push the image to a repository.
* `docker build --secret type=env,id=pypi-token,env=POETRY_PYPI_TOKEN_WEPOSITIVE_AWS -f Dockerfile . -t 354918389256.dkr.ecr.eu-west-1.amazonaws.com/fastapi-microservice-template:latest`
* `docker run -p 8000:8000 -it fastapi-microservice:latest`
