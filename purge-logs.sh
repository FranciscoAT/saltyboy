#!/bin/bash

CURRDIR=$(dirname "$(readlink -f "$0")")

remove_logs() {
    FULLPATH=${CURRDIR}/${1}/logs/
    echo "Purging all but the most recent ${1} logs..."
    rm `ls -t ${FULLPATH} | awk 'NR>7' | awk '{print "'${FULLPATH}'" $0; }'`
}

echo "-----------------"
date


remove_logs "db-wrapper"
remove_logs "twitch-bot"