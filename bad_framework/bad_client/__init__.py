"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.

Command-line client for the Benchmarking Anomaly Detection (BAD) framework.
"""
import argparse
import logging
import os
import re
import sys

from bad_framework.bad_utils.files import copy_files_to_bad_directory
from bad_framework.bad_utils.magic import BAD_CONF_DIR, LOG_FORMAT

from bad_framework.bad_client.cli import get_commands, handle_command

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bad.client")


def parse_config_file(config_filepath):
    if not os.path.exists(config_filepath):
        raise ValueError("Config file not found: '{}'", config_filepath)
    with open(config_filepath, "r") as config_file:
        key_value_pairs = [
            re.split(r"\s+", line.strip())
            for line in config_file
            if line.strip() and not line.startswith("#")
        ]
        loaded_settings = dict(key_value_pairs)
    return loaded_settings


def add_settings(runtime_config, loaded_settings):
    """Appends the loaded settings to runtime config, unless they are already defined.

    :param runtime_config: (dict) current runtime config.
    :param loaded_settings: (dict) additional config settings.
    :return: (dict) updated runtime config.
    """
    for key in loaded_settings.keys():
        if key not in runtime_config.keys():
            runtime_config[key] = loaded_settings[key]
    return runtime_config


def load_default_config(runtime_config):
    """Loads settings from a configuration file into the runtime configuration
    dictionary.

    Settings already defined in the runtime configuration are not overwritten.

    :param runtime_config: (dict) runtime configuration.
    :return: (dict) updated runtime configuration.
    """
    default_config_path = os.path.join(os.getcwd(), BAD_CONF_DIR)
    if os.path.exists(default_config_path):
        loaded_settings = parse_config_file(default_config_path)
        runtime_config = add_settings(runtime_config, loaded_settings)
    return runtime_config


def parse_arguments():
    """Defines and parses command-line arguments.

    The following positional arguments are required:
     - command

    The returned dictionary always contains the following boolean flag arguments:
     - bad.debug
     - bad.log.verbose

    Optional arguments non present on the command-line are not returned.

    See https://docs.python.org/3/library/argparse.html for details.

    :return: (dict) runtime configuration dictionary.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        type=str,
        choices=get_commands(),
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
        "-d",
        "--data",
        dest="bad.data",
        type=str,
        help="data set identifier",
    )
    parser.add_argument(
        "-o",
        "--dump-file",
        dest="bad.dump.file",
        type=str,
        help="path to output file",
    )
    parser.add_argument(
        "-p",
        "--parameters",
        dest="bad.candidate.parameters",
        type=str,
        help="path to Candidate parameters file",
    )
    parser.add_argument(
        "-q",
        "--requirements",
        dest="bad.candidate.requirements",
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
    parsed_args = vars(parser.parse_args())
    # Remove None-valued args
    for none_key in [k for k, v in parsed_args.items() if v is None]:
        del parsed_args[none_key]
    return parsed_args


def print_config(config):
    log.debug("Config = {")
    for k, v in config.items():
        log.debug("  %s = %r", k, v)
    log.debug("}")


def initialize_bad_directory():
    cwd = os.getcwd()
    bad_dir = os.path.join(cwd, ".bad")
    if not os.path.exists(bad_dir):
        os.mkdir(bad_dir)
        copy_files_to_bad_directory(bad_dir)


def main():
    config = parse_arguments()
    if config["bad.log.verbose"]:
        log.setLevel("DEBUG")

    initialize_bad_directory()

    config = load_default_config(config)
    print_config(config)

    command = config["command"]
    handle_command(command, config)

    sys.exit(0)


if __name__ == "__main__":
    main()
