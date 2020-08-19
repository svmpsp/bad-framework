"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import logging

from tornado.options import define, options
import tornado.httpserver
import tornado.ioloop
import tornado.web

from .views import IndexHandler, SetupHandler, RunHandler

# Define tornado options
define(
    "worker_home",
    default="/tmp/bad-framework",
    help="Working directory for the worker process.",
)
define("worker_port", default=3291, help="Port for the worker process.")
define("worker_debug", default=False, help="Activate development mode.")

# Define our own logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bad.server.worker")


class BADWorkerServer:
    def __init__(self, port, home_dir, debug):
        self._port = int(port)
        self._app = tornado.web.Application(
            [
                (r"/", IndexHandler),
                (r"/index.html", IndexHandler),
                (r"/setup/", SetupHandler),
                (r"/run/", RunHandler),
            ],
            debug=debug,
            worker_port=port,
            worker_home=home_dir,
        )
        self._server = tornado.httpserver.HTTPServer(
            self._app, max_buffer_size=524288000
        )

    def start(self):
        log.info(">>> Starting BAD worker on port %d", self._port)
        self._server.bind(self._port)
        self._server.start(1)
        tornado.ioloop.IOLoop.current().start()


def main():
    tornado.options.parse_command_line()

    bad_worker = BADWorkerServer(
        options.worker_port, options.worker_home, options.worker_debug
    )
    bad_worker.start()


if __name__ == "__main__":
    main()
