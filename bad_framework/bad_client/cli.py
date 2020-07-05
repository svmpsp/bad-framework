import datetime
import json
import logging
import subprocess

from bad_framework.bad_master import start_bad_master, stop_bad_master
from bad_framework.bad_worker import start_bad_worker, stop_bad_worker
from bad_framework.bad_utils.files import delete_bad_files
from bad_framework.bad_utils.network import HTTPSessionManager

from .monitor import monitor_suite
from .settings import *

log = logging.getLogger("bad.client")


def _load_workers(workers_filepath):

    with open(workers_filepath, "r") as workers_file:
        workers = []
        for line in workers_file:
            if line.strip() and not line.startswith("#"):
                worker_host, worker_port = line.strip().split(":")
                workers.append((worker_host, worker_port))
    return workers


def generate_suite_settings(config):
    workers = _load_workers(config["bad.workers"])
    return {
        "master_address": "{master_host}:{master_port}".format(
            master_host=config["bad.master.ip"], master_port=config["bad.master.port"]
        ),
        "data": config["bad.data"],
        "workers": workers,
        "seed": int(config["bad.experiment.seed"]),
        "trainset_size": float(config["bad.experiment.trainset_size"]),
    }


def download_dump_file(config, suite_id):
    dump_file_path = config[BAD_DUMP_FILE_KEY]
    log.info(">>> Saving suite dump to %s", dump_file_path)
    session_manager = HTTPSessionManager(
        domain="{master_hostname}:{master_port}".format(
            master_hostname=config[BAD_MASTER_KEY],
            master_port=config[BAD_MASTER_PORT_KEY],
        )
    )
    suite_dump_url = BAD_MASTER_SUITE_DUMP_TEMPLATE.format(suite_id)
    response = session_manager.get(suite_dump_url)

    with open(dump_file_path, "wb+") as dump_file:
        if response.status_code == 200:
            dump_file.write(response.content)
            log.info("<<< Dump file saved.")
        else:
            log.error("%s - %s", response.reason, suite_dump_url)


def _create_suite(config):
    log.info(">>> Generating experiment suite - BAD master at %s", config["bad.master"])

    master_hostname = "{0}:{1}".format(config["bad.master"], config["bad.master.port"],)
    master_session = HTTPSessionManager(domain=master_hostname)

    suite_settings = generate_suite_settings(config)
    encoded_settings = bytes(json.dumps(suite_settings), encoding="utf-8")

    log.info(">>> Submitting candidate %s", config[BAD_CANDIDATE_KEY])
    files = {
        "suite_settings": encoded_settings,
        "candidate_source": open(config[BAD_CANDIDATE_KEY], "rb").read(),
        "candidate_requirements": open(
            config[BAD_CANDIDATE_REQUIREMENTS_KEY], "rb"
        ).read(),
        "candidate_parameters": open(config[BAD_CANDIDATE_PARAMETERS_KEY], "rb").read(),
    }
    suite_submit_url = BAD_MASTER_SUITE_SUBMIT_URL
    suite_response = master_session.post_files(suite_submit_url, files=files)

    if suite_response.status_code == 200:
        log.info("<<< Experiment suite generated correctly.")
        return json.loads(suite_response.content)["suite_id"]
    else:
        raise ValueError("error generating suite - {}".format(suite_response.reason))


def _run_bad_suite(config):

    suite_id = _create_suite(config)

    master_address = "{master_ip}:{master_port}".format(
        master_ip=config["bad.master"], master_port=config["bad.master.port"]
    )
    master_session = HTTPSessionManager(master_address)
    start_time = datetime.datetime.now()
    monitor_suite(master_session=master_session, suite_id=suite_id)
    suite_execution_time = (datetime.datetime.now() - start_time).total_seconds()
    log.info("BAD execution completed in %f seconds.", suite_execution_time)
    download_dump_file(config, suite_id)


def _start_server(config):
    """Starts the BAD server processes.

    It starts a master process on localhost at the given port.
    It starts a worker process on each worker specified in the workers filepath.

    If debug is true, starts all processes in development mode.

    :param config: (dict) runtime configuration settings.
    :return: None
    """
    master_port = config["bad.master.port"]
    debug = config["bad.debug"]

    log.info(">>> Starting BAD master at localhost on port 3290")
    start_bad_master(master_port, debug)
    log.info("<<< Done.")

    workers_path = config["bad.workers"]
    workers = _load_workers(workers_path)
    for hostname, port in workers:
        log.info(">>> Starting BAD worker at %s on port %s", hostname, port)
        start_bad_worker(hostname, port, debug)
        log.info("<<< Done.")


def _stop_server(config):

    workers = _load_workers(config["bad.workers"])
    for hostname, port in workers:
        log.info(">>> Stopping BAD worker at %s on port %s", hostname, port)
        stop_bad_worker(hostname)
        log.info("<<< Done.")

    log.info(">>> Stopping BAD master at localhost")
    stop_bad_master()
    log.info("<<< Done.")


def handle_command(command, config):
    if command in bad_commands:
        bad_commands[command](config)
    else:
        raise ValueError("invalid command: {}".format(command))


def is_config_valid(config, command):
    """Checks if the the config dictionary contains all settings required to
    execute command.

    TODO: refactor me!

    If a setting is missing, raises a meaningful error message.

    :param config: (dict) argument dictionary.
    :param command: (string) command to validate.
    :return: None

    Examples:

    # >>> is_config_valid({})
    # Traceback (most recent call last):
    # ...
    # ValueError: missing required parameter bad.candidate. Specify it with the '-c' flag, as in:
    #     bad -c BAD.CANDIDATE
    """
    print(command)

    required_args = [(BAD_CANDIDATE_KEY, BAD_CANDIDATE_FLAG)]
    for param, flag in required_args:
        if param not in config:
            raise ValueError(
                """missing required parameter {param_name}. Specify it with the '{flag_name}' flag, as in:
    bad {flag_name} {upper_param_name}""".format(
                    param_name=param, flag_name=flag, upper_param_name=param.upper(),
                )
            )


def _restart_server(config):
    _stop_server(config)
    _start_server(config)


def _print_bad_processes(config):
    """
    TODO:
     - do some regexp matching and pretty output.
     - now shows ps process

    :param config:
    :return:
    """
    ps_proc = subprocess.Popen(["ps -au"], shell=True, stdout=subprocess.PIPE)
    for line in ps_proc.stdout:
        line = line.decode("utf-8").strip()
        if "bad_framework" in line:
            print(line)


def _clean_bad_files(config):
    delete_bad_files()


bad_commands = {
    "clean": _clean_bad_files,
    "ps": _print_bad_processes,
    "run": _run_bad_suite,
    "server-restart": _restart_server,
    "server-start": _start_server,
    "server-stop": _stop_server,
}


def get_commands():
    """Returns the commands available to the BAD CLI.

    :return: (dict_keys) available commands

    Examples:
    >>> cmds = list(get_commands()); cmds.sort(); cmds
    ['clean', 'ps', 'run', 'server-start', 'server-stop']
    """
    return bad_commands.keys()
