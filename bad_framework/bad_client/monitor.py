"""
TODO:
 - suite monitor is blocking
"""
import datetime
import logging
import time

from .ui import print_status_bar

log = logging.getLogger("bad.client")


def monitor_suite(master_session, suite_id, heartbeat_interval=1):
    """Monitors the suite execution from the client. Polls status updates
    at regular intervals and prints a status bar.

    :param master_session:
    :param suite_id:
    :param heartbeat_interval:
    :return:
    """
    log.info(">>> Starting run monitor")

    suite_experiments = master_session.get_json(
        "suite/{suite_id}/experiments/".format(suite_id=suite_id)
    )

    if suite_experiments:
        status_cache = {}
        for experiment in suite_experiments["experiments"]:
            status_cache[experiment["id"]] = experiment["status"]
            log.debug("Experiment %s - %s", experiment["id"], experiment["status"])
    else:
        raise ValueError("suite not found.")

    experiment_num = len(status_cache)
    start_ts = datetime.datetime.now()

    while True:
        suite_experiments = master_session.get_json(
            "suite/{}/experiments/".format(suite_id)
        )
        for experiment in suite_experiments["experiments"]:
            if status_cache[experiment["id"]] != experiment["status"]:
                log.debug("Experiment %s - %s", experiment["id"], experiment["status"])
                status_cache[experiment["id"]] = experiment["status"]
        completed_experiments_num = len(
            [status for status in status_cache.values() if status == "completed"]
        )
        failed_experiments_num = len(
            [status for status in status_cache.values() if status == "failed"]
        )
        print_status_bar(
            start_ts=start_ts,
            completed_num=completed_experiments_num,
            failed_num=failed_experiments_num,
            experiments_num=experiment_num,
        )
        if all(
            status == "completed" or status == "failed"
            for status in status_cache.values()
        ):
            break
        time.sleep(heartbeat_interval)
    log.info("<<< Run completed.")
