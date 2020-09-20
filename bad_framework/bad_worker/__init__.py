"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import logging
import os
import subprocess

from bad_framework.bad_utils.files import get_include_dir
import bad_framework

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def start_bad_worker(hostname, port, debug=False):

    package_bin_dir = "{include_dir}/bin".format(include_dir=get_include_dir())

    if debug:
        development_flags = "BAD_DEBUG=true BAD_PACKAGE={}".format(
            os.path.dirname(os.path.dirname(bad_framework.__file__))
        )
    else:
        development_flags = ""

    params = {
        "flag": development_flags,
        "script": os.path.join(package_bin_dir, "start_worker.sh"),
        "hostname": hostname,
        "port": port,
    }
    subprocess.call(
        ["{flag} source {script} {hostname} {port} > /dev/null".format(**params)],
        shell=True,
    )


def stop_bad_worker(hostname):
    package_bin_dir = "{include_dir}/bin".format(include_dir=get_include_dir())
    params = {
        "script": os.path.join(package_bin_dir, "stop_worker.sh"),
        "hostname": hostname,
    }
    subprocess.call(
        ["source {script} {hostname} > /dev/null".format(**params)],
        shell=True,
    )
