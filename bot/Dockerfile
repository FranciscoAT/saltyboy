FROM python:3.10-slim-buster

RUN apt update && apt upgrade -y && rm -rf /var/lb/apt/lists/*

WORKDIR /opt/bot

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /opt/logs

CMD alembic upgrade head && python main.py -lp /opt/logs
