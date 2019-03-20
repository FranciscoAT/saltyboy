#!/bin/bash

VENVDIR=venv
REQFILE=requirements.txt

echo "Remember to run this file like so!! . ./run-venv.sh"

if [ ! -d ${VENVDIR} ]; then
    echo "virtual environment directory doesn't exist, making venv..."
    virtualenv -p python3 ${VENVDIR}
    echo "venv created at ${VENVDIR}."
fi

echo "Entering virtual environment..."
source ${VENVDIR}/bin/activate

echo "Updating requirements from ${REQFILE}..."
pip install -r ${REQFILE}

echo "Remember you can quit the venv using the command: deactivate"