FROM python:3.12-slim-bullseye@sha256:c66cf219ac0083a9af2ff90e16530f16cd503c59eb7909feb3b8f3524dc1a87e as builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /home/nobody

ENV POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry"

# install dependencies
RUN apt-get update && apt-get -y upgrade \
    && apt-get install --no-install-recommends -y gcc curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install poetry
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# install project dependencies
COPY --chown=65534:65534 ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-root --only main

FROM python:3.12-slim-bullseye@sha256:c66cf219ac0083a9af2ff90e16530f16cd503c59eb7909feb3b8f3524dc1a87e

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && apt-get -y upgrade \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/nobody

RUN usermod -d /home/nobody nobody \
    && chown -R 65534:65534 /home/nobody
USER nobody

ENV PATH "/home/nobody/.venv/bin:$PATH"

COPY --from=builder --chown=65534:65534 /home/nobody/.venv /home/nobody/.venv
ENV PYTHONPATH "$PYTHONPATH:/home/nobody"
COPY --chown=65534:65534 src src
COPY --chown=65534:65534 config.env ./

CMD ["python", "src/main.py"]
