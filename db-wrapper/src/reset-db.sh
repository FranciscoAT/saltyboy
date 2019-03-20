#!/bin/bash

source setup-scripts/venv/bin/activate
python3 setup-scripts/setup-tables.py --dump --reset

if [ ! -z ${1} ]; then
    python3 setup-scripts/setup-tables.py --populate ${1}
fi

