"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import datetime
import logging
import time

from bad_framework.bad_client.ui import print_status_bar
from bad_framework.bad_utils.adt import ExperimentStatus

log = logging.getLogger("bad.client")


def initialize_status_cache(suite_experiments):
    if not suite_experiments:
        raise ValueError("suite not found.")
    status_cache = {}
    for experiment in suite_experiments:
        status_cache[experiment["id"]] = experiment["status"]
    return status_cache


def get_suite_experiments(master_session, suite_id):
    suite_status_url = "suite/{suite_id}/status/".format(suite_id=suite_id)
    suite_status = master_session.get_json(suite_status_url)
    if not suite_status:
        raise ValueError("suite not found.")
    return suite_status["experiments"]


def get_count_by_status(status_cache, query_status):
    if not status_cache:
        raise ValueError("invalid status cache: {}".format(status_cache))
    if query_status not in ExperimentStatus.valid_statuses():
        raise ValueError("invalid status: {}", query_status)
    experiments_with_status = [
        status for status in status_cache.values() if status == query_status
    ]
    return len(experiments_with_status)


def update_status_cache(suite_experiments, status_cache):
    for experiment in suite_experiments:
        if status_cache[experiment["id"]] != experiment["status"]:
            status_cache[experiment["id"]] = experiment["status"]


def monitor_suite(master_session, suite_id, heartbeat_interval=1):
    """Monitors the suite execution from the client. Polls status updates
    at regular intervals and prints a status bar.

    :param master_session:
    :param suite_id: (string) suite identifier.
    :param heartbeat_interval:
    :return: None
    """
    log.info(">>> Starting run monitor")
    suite_experiments = get_suite_experiments(master_session, suite_id)
    status_cache = initialize_status_cache(suite_experiments)

    total = len(status_cache)
    start_ts = datetime.datetime.now()

    while True:
        suite_experiments = get_suite_experiments(master_session, suite_id)
        update_status_cache(suite_experiments, status_cache)
        completed = get_count_by_status(status_cache, "completed")
        failed = get_count_by_status(status_cache, "failed")
        print_status_bar(
            start_ts=start_ts,
            completed_num=completed,
            failed_num=failed,
            experiments_num=total,
        )
        # If the suite is completed break
        if all(
            status == "completed" or status == "failed"
            for status in status_cache.values()
        ):
            print()  # Print a newline to skip over the status bar
            break
        # Otherwise, wait and retry
        time.sleep(heartbeat_interval)
    log.info("<<< Run completed.")
