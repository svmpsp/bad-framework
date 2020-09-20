"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import logging

from tornado.options import define, options
import tornado.httpserver
import tornado.ioloop
import tornado.web

from .views import (
    CandidateHandler,
    DatasetHandler,
    ExperimentHandler,
    IndexHandler,
    ResultHandler,
    SuiteHandler,
    SuiteDumpHandler,
    SuiteStatusHandler,
)

# Define tornado options
define(
    "master_home",
    default="/tmp/bad-framework",
    help="Working directory for the master process.",
)
define("master_port", default=3290, help="Port for the master process.")
define("master_debug", default=False, help="Activate development mode.")

# Define our own logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bad.server.master")


class BADMasterServer:
    def __init__(self, port, home_dir):
        self._port = int(port)
        self._app = tornado.web.Application(
            [
                (r"^/$", IndexHandler),
                (r"^/index.html$", IndexHandler),
                (r"^/candidate/(?P<candidate_id>[a-z0-9-]+)/$", CandidateHandler),
                (
                    r"^/candidate/(?P<candidate_id>[a-z0-9-]+)/requirements/$",
                    CandidateHandler,
                ),
                (r"^/dataset/(?P<dataset_name>[a-z0-9-]+)/$", DatasetHandler),
                (r"^/experiment/(?P<experiment_id>[a-z0-9-]+)/$", ExperimentHandler),
                (
                    r"^/experiment/(?P<experiment_id>[a-z0-9-]+)/results/$",
                    ResultHandler,
                ),
                (
                    r"^/experiment/(?P<experiment_id>[a-z0-9-]+)/metrics.json$",
                    ResultHandler,
                ),
                (r"^/experiment/(?P<experiment_id>[a-z0-9-]+)/roc.png$", ResultHandler),
                (r"^/suite/$", SuiteHandler),
                (r"^/suite/(?P<suite_id>[a-z0-9-]+)/$", SuiteHandler),
                (r"^/suite/(?P<suite_id>[a-z0-9-]+)/dump/$", SuiteDumpHandler),
                (
                    r"^/suite/(?P<suite_id>[a-z0-9-]+)/status/$",
                    SuiteStatusHandler,
                ),
            ],
            debug=options.master_debug,
            master_home=home_dir,
            master_port=self._port,
        )
        self._server = tornado.httpserver.HTTPServer(
            self._app, max_buffer_size=524288000
        )

    def start(self):
        log.info(">>> Starting BAD master on port %d", self._port)
        self._server.bind(self._port)
        self._server.start(1)
        tornado.ioloop.IOLoop.current().start()


def main():
    tornado.options.parse_command_line()

    log.info("Starting BAD master with the following options:")
    for k, v in options.items():
        log.info("  %s = %r", k, v)

    bad_master = BADMasterServer(options.master_port, options.master_home)
    bad_master.start()


if __name__ == "__main__":
    main()
