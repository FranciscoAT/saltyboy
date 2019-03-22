#!/bin/bash

PIDWRAPPER=$(ps -ef | grep "[s]h -c node src/index.js" | awk '{print $2}')
PIDTWITCH=$(ps -ef | grep "[s]h -c node src/bot.js" | awk '{print $2}')
CURRDIR=$(dirname "$(readlink -f "$0")")
WEBHOOK=${1}
SESSION="saltybot"

echo "-----------------"
date

if [ -z ${PIDWRAPPER} ] && [ -z ${PIDTWITCH} ]; then
    echo "Both things are down assume down for a reason ignore."
    exit 0
fi

kill_process() {
    if [ ! -z ${1} ]; then
        echo "Killing process ${1}"
        kill -9 ${1}
    else
        echo "No process to kill."
    fi
}

kill_children () {
    CPIDWRAPPER=$(ps -ef | grep "[n]ode src/index.js" | awk '{print $2}')
    CPIDTWITCH=$(ps -ef | grep "[n]ode src/bot.js" | awk '{print $2}')

    echo "Killing DB Wrapper child process if exists"
    kill_process ${CPIDWRAPPER}

    echo "Killing Twitch Bot child process if exists"
    kill_process ${CPIDTWITCH}
}

send_alert () {
    curl -X POST ${WEBHOOK} --data content="Restarting Saltybot"
}

kill_process ${PIDWRAPPER}
kill_process ${PIDTWITCH}
kill_children

echo "Killing tmux session"
tmux kill-session -t ${SESSION}

echo "Re running with logs"
send_alert

${CURRDIR}/run-with-logs.sh