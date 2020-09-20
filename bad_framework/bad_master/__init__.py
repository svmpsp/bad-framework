"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import os
import subprocess

from bad_framework.bad_utils.files import get_include_dir


def start_bad_master(port, debug=False):
    """Starts the BAD master process on localhost at the given port.

    If debug is True, starts the master in development mode.

    :param port: (int) port to start the server on.
    :param debug: (bool) True if master must be started in
    development mode, False otherwise.
    :return: None
    """
    package_bin_dir = "{include_dir}/bin".format(include_dir=get_include_dir())
    params = {
        "flag": "BAD_DEBUG=true" if debug else "",
        "script": os.path.join(package_bin_dir, "start_master.sh"),
        "port": port,
    }
    subprocess.call(
        ["{flag} source {script} {port} > /dev/null".format(**params)],
        shell=True,
    )


def stop_bad_master():
    """Stops the BAD master process on localhost."""
    package_bin_dir = "{include_dir}/bin".format(include_dir=get_include_dir())
    subprocess.call(
        [
            "source {script} > /dev/null".format(
                script=os.path.join(package_bin_dir, "stop_master.sh")
            )
        ],
        shell=True,
    )
