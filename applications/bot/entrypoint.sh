#!/bin/bash

set -e

poetry run alembic upgrade head
poetry run python main.py --logs "$LOG_PATH"