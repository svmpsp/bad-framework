# Copyright (c) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>. All rights reserved.
"""
Command-line client for the Benchmarking Anomaly Detection (BAD) framework.

 TODO:
  - implement rescheduling of failed experiments.
  - fix spark candidate in master/index, it does not keep track of old candidates.
  - preliminary repartion Spark candidates to reduce task size.
  - write conf validator for required parameters.
  - move all validation to master.
  - master host is not consistent between bin/scripts.sh and bad-client.
  - manage connection errors in client.
  - set global config in server procs (master_url, runner_id, etc.).
"""
import argparse
import logging
import os
import re
import sys

from bad_framework.bad_utils.files import init_working_directory, is_directory_init

from .cli import get_commands, handle_command

DEFAULT_PARAMETERS = {
    "bad.candidate.parameters": "candidate_parameters.txt",
    "bad.candidate.requirements": "candidate_requirements.txt",
    "bad.default.conf": "conf/defaults.conf",
    "bad.dump.file": "bad_dump.csv",
}


def load_default_config(runtime_config):
    """Loads settings from a configuration file into the runtime configuration
    dictionary.

    Settings already defined in the runtime configuration are not overwritten.

    :param runtime_config: (dict) runtime configuration.
    :return: (dict) updated runtime configuration.
    """
    default_config_path = os.path.join(
        os.getcwd(), DEFAULT_PARAMETERS["bad.default.conf"],
    )
    if os.path.exists(default_config_path):
        with open(default_config_path, "r") as config_file:
            key_value_pairs = [
                re.split(r"\s+", line.strip())
                for line in config_file
                if line.strip() and not line.startswith("#")
            ]
            loaded_settings = dict(key_value_pairs)
        for key in loaded_settings.keys():
            if key not in runtime_config.keys():
                runtime_config[key] = loaded_settings[key]
    return runtime_config


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        type=str,
        choices=get_commands(),
        default=None,
        help="BAD framework command",
    )
    parser.add_argument(
        "-c",
        "--candidate",
        dest="bad.candidate",
        type=str,
        help="path to Candidate implementation",
    )
    parser.add_argument(
        "-d", "--data", dest="bad.data", type=str, help="data set identifier"
    )
    parser.add_argument(
        "-o",
        "--dump-file",
        dest="bad.dump.file",
        default=DEFAULT_PARAMETERS["bad.dump.file"],
        type=str,
        help="path to output file",
    )
    parser.add_argument(
        "-p",
        "--parameters",
        dest="bad.candidate.parameters",
        default=DEFAULT_PARAMETERS["bad.candidate.parameters"],
        type=str,
        help="path to Candidate parameters file",
    )
    parser.add_argument(
        "-q",
        "--requirements",
        dest="bad.candidate.requirements",
        default=DEFAULT_PARAMETERS["bad.candidate.requirements"],
        type=str,
        help="path to Candidate requirements.txt file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="bad.log.verbose",
        help="enables debug logging",
    )
    parser.add_argument(
        "-D",
        "--dev",
        action="store_true",
        dest="bad.debug",
        help="run the framework in development mode",
    )
    return parser.parse_args()


def print_config(config):
    log = config["log"]
    log.debug("Config = {")
    for k, v in config.items():
        log.debug("  %s = %r", k, v)
    log.debug("}")


def main():
    config = vars(parse_arguments())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger("bad.client")

    if config["bad.log.verbose"]:
        log.setLevel("DEBUG")

    cwd = os.getcwd()

    if not is_directory_init(cwd):
        init_working_directory(cwd)

    config = load_default_config(config)
    config["log"] = log

    print_config(config)

    command = config["command"]

    if command:
        handle_command(command, config)
    else:
        log.error(
            "You must specify a command. Available commands are: %s",
            ", ".join(get_commands()),
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
