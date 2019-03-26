#!/bin/bash
CURRDIR=$(dirname "$(readlink -f "$0")")


source venv/bin/activate
python3 setup-tables.py --dump --reset

if [ -z ${1} ]; then
    NEWESTDUMP=dumps/$(ls -t ${CURRDIR}/dumps | head -1)
else
    NEWESTDUMP=${1}
fi

python3 setup-tables.py --populate ${NEWESTDUMP}

