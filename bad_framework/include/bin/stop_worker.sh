#!/usr/bin/env bash
# Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.
# All rights reserved.

if [ ! "$#" -eq 1 ]; then
  echo "Usage: stop_worker.sh BAD_WORKER_HOST";
  exit 1;
fi

BAD_WORKER_HOST="$1"
BAD_WORKER_HOME='/tmp/bad-framework'

if ssh -qT "$BAD_WORKER_HOST" "[ -d $BAD_WORKER_HOME ]" < /dev/null; then
  ssh -qT "$BAD_WORKER_HOST" <<REMOTE_SCRIPT
  WORKER_PIDS="\$(ps aux | grep '[b]ad_framework.bad_worker.server' | awk '{ print \$2; }')"
  for WORKER_PID in \$WORKER_PIDS; do
    kill "\$WORKER_PID"
  done
REMOTE_SCRIPT

  ssh -qT "$BAD_WORKER_HOST" "rm -rf $BAD_WORKER_HOME" < /dev/null

fi

exit 0
