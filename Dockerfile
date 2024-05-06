FROM python:3.12.2-slim-bullseye as base
RUN apt-get update
RUN pip install poetry==1.7.1

WORKDIR app/
COPY src src/
COPY README.md poetry.toml pyproject.toml poetry.lock ./

RUN poetry install --no-root # Do not install the root package (your project).

FROM base as production
RUN poetry install --no-interaction --no-ansi --without dev
WORKDIR app/
ENTRYPOINT poetry run python -m sample_app
