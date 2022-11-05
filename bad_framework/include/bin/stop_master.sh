#!/usr/bin/env bash
# Copyright (C) 2020 Sivam Pasupathipillai <sivam.pasupathipillai@gmail.com>.
# All rights reserved.

kill_master_processes () {
  # Deletes all BAD master active processes
  ps aux | grep '[b]ad_framework.bad_master.server' | awk '{ print $2; }' | while read -r MASTER_PID;
  do
    if [ ! -z "$MASTER_PID" ]; then
      kill "$MASTER_PID";
    fi
  done
}

delete_bad_work_dir () {
  # Removes BAD working directory from master host
  BAD_MASTER_HOME='/tmp/bad-framework'
  if [ -d "$BAD_MASTER_HOME" ]; then
    rm -rf "$BAD_MASTER_HOME"
  fi
}

kill_master_processes
delete_bad_work_dir
exit 0
