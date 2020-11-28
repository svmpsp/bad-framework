"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import datetime
import json
import logging
import os

from bad_framework.bad_master import start_bad_master, stop_bad_master
from bad_framework.bad_worker import start_bad_worker, stop_bad_worker
from bad_framework.bad_utils.adt import CandidateSpec, DataSpec
from bad_framework.bad_utils.files import (
    parse_parameters,
    parse_requirements,
)
from bad_framework.bad_utils.network import HTTPSessionManager

from .monitor import monitor_suite

log = logging.getLogger("bad.client")


def _add_default_parameters(parameters_list, config):
    """

    >>> params = [("a", 1), ("b", 2)]
    >>> config = {"bad.experiment.seed": 42, "bad.experiment.trainset_size": 1.0}
    >>> _add_default_parameters(params, config)
    [('a', 1), ('b', 2), ('seed', 42), ('trainset_size', 1.0)]

    """
    parameters_list.append(("seed", config["bad.experiment.seed"]))
    parameters_list.append(("trainset_size", config["bad.experiment.trainset_size"]))
    return parameters_list


def _create_suite(config):
    """Hello world!

    TODO:
     - documentation
    :param config:
    :return:
    """
    log.info(">>> Generating experiment suite - BAD master at %s", config["bad.master"])

    suite_settings = _generate_suite_settings(config)

    candidate_spec = suite_settings["candidate"]
    data_spec = suite_settings["data"]

    files = {}

    if candidate_spec.source == "local":
        log.info(">>> Submitting local candidate %s", candidate_spec.url)
        with open(candidate_spec.url, "rb") as local_candidate_file:
            candidate_content = local_candidate_file.read()
        suite_settings["candidate_requirements"] = parse_requirements(
            config["bad.candidate.requirements"]
        )
        files["candidate_source"] = candidate_content

    if data_spec.source == "local":
        log.info(">>> Submitting local dataset %s", data_spec.url)
        with open(data_spec.url, "rb") as local_dataset_file:
            dataset_content = local_dataset_file.read()
        files["data_source"] = dataset_content

    encoded_settings = bytes(json.dumps(suite_settings), encoding="utf-8")
    files["suite_settings"] = encoded_settings

    master_hostname = "{hostname}:{port}".format(
        hostname=config["bad.master"],
        port=config["bad.master.port"],
    )
    master_session = HTTPSessionManager(domain=master_hostname)

    suite_submit_url = "suite/"
    suite_response = master_session.post_files(suite_submit_url, files=files)

    if suite_response.status_code == 200:
        response_message = json.loads(suite_response.content)
        if response_message["status"] == 200:
            log.info("<<< Experiment suite generated correctly.")
            return response_message["suite_id"]
        else:
            raise ValueError(
                "error generating suite - {}".format(response_message["error"])
            )
    else:
        raise ValueError("internal server error {}".format(suite_response.status_code))


def _generate_suite_settings(config):
    """Generates JSON-encoded suite settings to be sent to the master.

    :param config:
    :return:
    """
    workers = _load_workers(config["bad.workers"])
    candidate_spec = _load_candidate_spec(config["bad.candidate"])
    data_spec = _load_data_spec(config["bad.data"])
    parameters_list = parse_parameters(config["bad.candidate.parameters"])
    parameters_list = _add_default_parameters(parameters_list, config)

    return {
        "candidate": candidate_spec,
        "candidate_parameters": parameters_list,
        "data": data_spec,
        "master_address": "{master_host}:{master_port}".format(
            master_host=config["bad.master.ip"], master_port=config["bad.master.port"]
        ),
        "workers": workers,
    }


def _download_dump_file(config, suite_id):
    dump_file_path = config["bad.dump.file"]
    log.info(">>> Saving suite dump to %s", dump_file_path)
    session_manager = HTTPSessionManager(
        domain="{master_hostname}:{master_port}".format(
            master_hostname=config["bad.master"],
            master_port=config["bad.master.port"],
        )
    )
    suite_dump_url = "suite/{sid}/dump/".format(sid=suite_id)
    response = session_manager.get(suite_dump_url)

    with open(dump_file_path, "wb+") as dump_file:
        if response.status_code == 200:
            dump_file.write(response.content)
            log.info("<<< Dump file saved.")
        else:
            log.error("%s - %s", response.reason, suite_dump_url)


def _load_candidate_spec(candidate_url):
    if os.path.isfile(candidate_url):
        return CandidateSpec("local", candidate_url)
    else:
        return CandidateSpec("remote", candidate_url)


def _load_data_spec(data_url):
    if os.path.isfile(data_url):
        return DataSpec("local", data_url)
    else:
        return DataSpec("remote", data_url)


def _load_workers(workers_filepath):

    with open(workers_filepath, "r") as workers_file:
        workers = []
        for line in workers_file:
            if line.strip() and not line.startswith("#"):
                worker_host, worker_port = line.strip().split(":")
                workers.append((worker_host, worker_port))
    return workers


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
    _download_dump_file(config, suite_id)


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


def _validate_config(command, config):
    """Validates the config settings for a given command. Returns True if the config
    is valid, raises an exception otherwise.

    >>> config = {"bad.workers": [("localhost", "1234")]}
    >>> _validate_config("server-stop", config)

    >>> _validate_config("server-stop", {})
    Traceback (most recent call last):
        ...
    ValueError: parameter ...

    :param command: (string)
    :param config: (dict)
    """
    required_keys = {
        "run": [
            "bad.candidate",
            "bad.candidate.parameters",
            "bad.data",
            "bad.experiment.seed",
            "bad.experiment.trainset_size",
            "bad.master",
            "bad.master.ip",
            "bad.master.port",
            "bad.workers",
        ],
        "server-start": ["bad.debug", "bad.master.port", "bad.workers"],
        "server-stop": ["bad.workers"],
    }
    for key in required_keys[command]:
        if key not in config:
            raise ValueError("parameter '{key}' is required.".format(key=key))


bad_commands = {
    "run": _run_bad_suite,
    "server-start": _start_server,
    "server-stop": _stop_server,
}


def get_commands():
    """Returns the commands available to the BAD CLI.

    :return: (dict_keys) available commands

    Examples:
    >>> cmds = list(get_commands()); cmds.sort(); cmds
    ['run', 'server-start', 'server-stop']
    """
    return bad_commands.keys()


def handle_command(command, config):
    _validate_config(command, config)
    bad_commands[command](config)
