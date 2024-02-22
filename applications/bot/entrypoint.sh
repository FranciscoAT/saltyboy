#!/bin/bash

set -e

LOG_PATH=
DEBUG=

while getopts "l:d" name; do
    case $name in 
        l) LOG_PATH="$OPTARG";;
        d) DEBUG=1;;
        *) exit 1;;
    esac
done

poetry run alembic upgrade head
poetry run python main.py ${LOG_PATH:+"--logs"} "$LOG_PATH" ${DEBUG+:"--debug"}