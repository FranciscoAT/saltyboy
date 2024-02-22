#!/bin/bash

set -e

poetry run alembic upgrade head
poetry run python main.py ${LOG_PATH:+"--logs"} "$LOG_PATH"