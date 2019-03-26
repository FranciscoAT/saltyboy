#!/bin/bash

SESSION="saltybot"
PIDWRAPPER=$(ps -ef | grep "[s]h -c node src/index.js" | awk '{print $2}')
PIDTWITCH=$(ps -ef | grep "[s]h -c node src/bot.js" | awk '{print $2}')
PIDTMUX=$(ps -ef | grep "[t]mux new-session -s ${SESSION} -d" | awk '{print $2}')
TMUXLS=$(tmux ls | grep "${SESSION}" | awk '{print $1}')
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

    echo "Killing tmux process if exists"
    kill_process ${PIDTMUX}
}


if [ -z ${PIDWRAPPER} ] && [ -z ${PIDTWITCH} ] && [ -z ${TMUXLS} ]; then
    echo "Both things are down assume down for a reason ignore."
    echo "Killing children for safety."
    kill_children
    exit 0
elif [ ! -z ${PIDWRAPPER} ] && [ ! -z ${PIDTWITCH} ] && [ ! -z ${TMUXLS} ]; then
    echo "Services are running fine."
    exit 0
else
    echo "Something is wrong shutting everything down."
    kill_process ${PIDWRAPPER}
    kill_process ${PIDTWITCH}

    if [ ! -z ${TMUXLS} ]; then
        echo "killing tmux"
        tmux kill-session -t ${SESSION}
    fi

    sleep 2
    echo "killing children"
    kill_children
    send_alert
fi
