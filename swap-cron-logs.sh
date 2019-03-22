#!/bin/bash

CURRDIR=$(dirname "$(readlink -f "$0")")

cp ${CURRDIR}/logs/cron-logs.log ${CURRDIR}/logs/cron-logs.tmp.log
cp ${CURRDIR}/logs/cron-logs-restart.log ${CURRDIR}/logs/cron-logs-restart.tmp.log
> ${CURRDIR}/logs/cron-logs.log
> ${CURRDIR}/logs/cron-logs-restart.log
