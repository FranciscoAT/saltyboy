#!/bin/bash

RUNTIME=$(date +%F_%H-%M-%S)
LOGSFILE=logs/${RUNTIME}
SESSION="saltybot"

send_to_env () {
    tmux send -t ${SESSION} "${1}" ENTER
}


run_environment () {
    send_to_env "cd ${1}"
    send_to_env "npm install"
    send_to_env "npm run start-prod &> ${LOGSFILE}.log"
}

tmux new-session -s ${SESSION} -d
run_environment db-wrapper
tmux split-window -h
run_environment twitch-bot

if [ "${1}" == "-a" ]; then
    tmux -2 attach-session -d
fi

