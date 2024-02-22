FROM python:3.11

ARG USER_ID
ARG GROUP_ID

ENV LOG_PATH=/opt/logs/
ENV DEBUG=

# Update the image
RUN apt update \
    && apt upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Run the application as a non-root User
RUN useradd -m -d /home/user -u $USER_ID user
USER $USER_ID:$GROUP_ID
ENV PATH="$PATH:/home/user/.local/bin"

WORKDIR /opt/bot

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Install Depenencies
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN poetry install --no-root --without=dev

COPY src src
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY main.py main.py
COPY entrypoint.sh entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh", "-l", $LOG_PATH, ${DEBUG:+"-d"}]
