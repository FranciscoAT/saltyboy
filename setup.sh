#!/bin/bash

session="saltybot"
tmux new-session -s ${session} -d
tmux send -t ${session} "cd db-wrapper; npm install; npm run start-dev" ENTER
tmux split-window -h
tmux send -t ${session} "cd twitch-bot; npm install; npm run start-dev" ENTER
tmux -2 attach-session -d
