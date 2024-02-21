FROM python:3.10-slim-buster

# Update the image
RUN apt update \
    && apt upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/bot

COPY . .

RUN pip install --upgrade pip

# Generate the requirements.txt file through Python Poetry
RUN pip install poetry==1.4.2 \
    && poetry export -f requirements.txt --output requirements.txt --without dev

# Install dependencies
RUN pip install -r requirements.txt

# Create log output, this directory is volume mounted in the `docker-compose.yml` file
RUN mkdir -p /opt/logs

CMD alembic upgrade head \
    && python main.py -lp /opt/logs
