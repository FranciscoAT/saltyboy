#!/bin/bash

PIDWRAPPER=$(ps -ef | grep "[s]h -c node src/index.js" | awk '{print $2}')
PIDTWITCH=$(ps -ef | grep "[s]h -c node src/bot.js" | awk '{print $2}')
WEBHOOK=${1}

kill_process() {
    if [ ! -z ${1} ]; then
        echo "Killing process ${1}"
        kill -9 ${1}
    else
        echo "No process to kill."
    fi
}


send_alert () {
    curl -X POST ${WEBHOOK} --data content="@everyone Saltybot is down!"
}

kill_children () {
    CPIDWRAPPER=$(ps -ef | grep "[n]ode src/index.js" | awk '{print $2}')
    CPIDTWITCH=$(ps -ef | grep "[n]ode src/bot.js" | awk '{print $2}')

    echo "Killing DB Wrapper child process if exists"
    kill_process ${CPIDWRAPPER}

    echo "Killing Twitch Bot child process if exists"
    kill_process ${CPIDTWITCH}
}

if [ -z ${PIDWRAPPER} ] && [ -z ${PIDTWITCH} ]; then
    echo "Both things are down assume down for a reason ignore."
    echo "Killing children for safety."
    kill_children
    exit 0
fi

if [ -z ${PIDWRAPPER} ]; then
    echo "DB Wrapper Server is down, killing twitch bot and children."
    kill_process ${PIDWRAPPER}
    sleep 5
    kill_children
    send_alert
elif [ -z ${PIDTWITCH} ]; then
    ehco "Twitch Bot is down, killing DB Wrapper and children"
    kill_process ${PIDTWITCH}
    sleep 5
    kill_children
    send_alert
else
    echo "Services are running fine"
fi
