#!/usr/bin/env bash
# Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.
# All rights reserved.

if [ "$#" -ne 2 ]; then
  echo "Usage: start_worker.sh BAD_WORKER_HOST BAD_WORKER_PORT";
  exit 1
fi

if [ "$BAD_DEBUG" ]; then
  DEBUG_FLAG='debug=True'
else
  DEBUG_FLAG='debug=False'
fi

if [ "$BAD_DEBUG" = true ]; then
  # Running in development mode, install package from local path
  echo "Starting BAD in development mode..."

  if [[ -z "$BAD_PACKAGE" ]]; then
    echo "BAD_PACKAGE is not defined. Cannot start worker in development mode."
    exit 1
  fi

  BAD_WORKER_HOST="$1"
  BAD_WORKER_PORT="$2"

  BAD_WORKER_HOME='/tmp/bad-framework'
  LOGS_DIR="$BAD_WORKER_HOME/logs"

  echo "Creating remote directories..."
  ssh -qT "$BAD_WORKER_HOST" "if [ ! -d $LOGS_DIR ]; then mkdir -p $LOGS_DIR; fi" < /dev/null

  echo "Setting up BAD worker virtualenv..."
  VENV_DIR="$BAD_WORKER_HOME/envs/bad_worker_$BAD_WORKER_PORT"

  ssh -qT "$BAD_WORKER_HOST" <<REMOTE_SCRIPT
  virtualenv "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip
  pip install --upgrade "$BAD_PACKAGE"
REMOTE_SCRIPT

  echo "Starting BAD worker..."
  ssh -qT "$BAD_WORKER_HOST" <<REMOTE_SCRIPT
  source "$VENV_DIR/bin/activate"
  BAD_WORKER_LOG="$LOGS_DIR/bad-worker_$BAD_WORKER_PORT.log"
  echo Logging to \$BAD_WORKER_LOG
  nohup python3 -m bad_framework.bad_worker.server \
    worker_port="$BAD_WORKER_PORT" \
    worker_home="$BAD_WORKER_HOME" \
    "$DEBUG_FLAG" > \$BAD_WORKER_LOG 2>&1 < /dev/null &
REMOTE_SCRIPT

  exit 0;

else
  # Running in normal mode, download package version from PyPI
  BAD_WORKER_HOST="$1"
  BAD_WORKER_PORT="$2"

  BAD_WORKER_HOME='/tmp/bad-framework'
  LOGS_DIR="$BAD_WORKER_HOME/logs"

  echo "Creating remote directories..."
  ssh -qT "$BAD_WORKER_HOST" "if [ ! -d $LOGS_DIR ]; then mkdir -p $LOGS_DIR; fi" < /dev/null

  echo "Setting up BAD worker virtualenv..."
  VENV_DIR="$BAD_WORKER_HOME/envs/bad_worker_$BAD_WORKER_PORT"

  ssh -qT "$BAD_WORKER_HOST" <<REMOTE_SCRIPT
  virtualenv  "$VENV_DIR"
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip
  pip install --upgrade bad-framework
REMOTE_SCRIPT

  echo "Starting BAD worker..."

  ssh -qT "$BAD_WORKER_HOST" <<REMOTE_SCRIPT
  source "$VENV_DIR/bin/activate"
  BAD_WORKER_LOG="$LOGS_DIR/bad-worker_$BAD_WORKER_PORT.log"
  echo Logging to \$BAD_WORKER_LOG
  nohup python3 -m bad_framework.bad_worker.server \
    worker_home="$BAD_WORKER_HOME" \
    worker_port="$BAD_WORKER_PORT" \
    "$DEBUG_FLAG" > \$BAD_WORKER_LOG 2>&1 < /dev/null &
REMOTE_SCRIPT

  exit 0;
fi
