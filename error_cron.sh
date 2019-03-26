#!/bin/bash

PIDWRAPPER=$(ps -ef | grep "[s]h -c node src/index.js" | awk '{print $2}')
PIDTWITCH=$(ps -ef | grep "[s]h -c node src/bot.js" | awk '{print $2}')
PIDTMUX=$(ps -ef | grep "[t]mux new-session -s saltybot -d" | awk '{print $2}')
SESSION="saltybot"
WEBHOOK=${1}

echo "-----------------"
date

kill_process() {
    if [ ! -z ${1} ]; then
        echo "Killing process ${1}"
        kill -9 ${1}
    else
        echo "No process to kill."
    fi
}


send_alert () {
    curl -X POST ${WEBHOOK} --data content="@everyone Saltybot is down!" --silent
}

kill_children () {
    CPIDWRAPPER=$(ps -ef | grep "[n]ode src/index.js" | awk '{print $2}')
    CPIDTWITCH=$(ps -ef | grep "[n]ode src/bot.js" | awk '{print $2}')

    echo "Killing DB Wrapper child process if exists"
    kill_process ${CPIDWRAPPER}

    echo "Killing Twitch Bot child process if exists"
    kill_process ${CPIDTWITCH}
}

if [ -z ${PIDWRAPPER} ] && [ -z ${PIDTWITCH} ] && [ -z ${PIDTMUX} ]; then
    echo "Both things are down assume down for a reason ignore."
    echo "Killing children for safety."
    kill_children
    exit 0
elif [ ! -z ${PIDWRAPPER} ] && [ ! -z ${PIDTWITCH} ] && [ ! -z ${PIDTMUX} ]; then
    echo "Services are running fine."
else
    echo "Something is wrong shutting everything down."
    kill_process ${PIDWRAPPER}
    kill_process ${PIDTWITCH}
    tmux kill-session -t ${SESSION}
    sleep 5
    kill_children
    send_alert    
fi

