FROM python:3.10-slim-buster

RUN apt update & apt upgrade -y

WORKDIR /opt/web

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /opt/logs

CMD python main.py -lp /opt/logs
