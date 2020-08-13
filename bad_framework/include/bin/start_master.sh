#!/usr/bin/env bash
# Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.
# All rights reserved.

if [ ! "$#" -eq 1 ]; then
  echo "Usage: start_master.sh BAD_MASTER_PORT";
  exit 1;
fi

function check_bad_master {
  # Checks if the BAD master has already been started
  BAD_MASTER_PIDS="$( ps aux | grep '[b]ad_framework.bad_master.server' | awk '{ print $2; }' )"
  if [ ! -z "$BAD_MASTER_PIDS" ]; then
    echo "BAD master already started. Nothing to do."
    exit 1
  fi
}

check_bad_master

BAD_MASTER_PORT="$1"
BAD_HOME="$(pwd)/.bad"  # Working directory where to store logs and intermediate files.
BAD_MASTER_HOME='/tmp/bad-framework'  # Server working directory where to store server files.
LOGS_DIR="$BAD_HOME/logs"
BAD_MASTER_LOG="$LOGS_DIR/bad-master_$BAD_MASTER_PORT.log"

if [ "$BAD_DEBUG" ]; then
  DEBUG_FLAG='debug=True'
else
  DEBUG_FLAG='debug=False'
fi

if [ ! -d "$BAD_MASTER_HOME" ]; then
  mkdir -p "$BAD_MASTER_HOME"
fi

if [ ! -d "$LOGS_DIR" ]; then
  mkdir -p "$LOGS_DIR"
fi

echo "Logging to $BAD_MASTER_LOG"
nohup python3 -m bad_framework.bad_master.server \
  master_port="$BAD_MASTER_PORT" \
  master_home="$BAD_MASTER_HOME" \
  "$DEBUG_FLAG" > "$BAD_MASTER_LOG" 2>&1 < /dev/null &

exit 0
