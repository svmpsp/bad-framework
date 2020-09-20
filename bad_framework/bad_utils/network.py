"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from tempfile import NamedTemporaryFile
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler
import httpx
import json
import random
import requests

from .files import save_file


class HTTPSessionManager:
    """Utility class for managing a persistent HTTP session."""

    def __init__(self, domain):
        """Initializes the SessionManager to connect to a given hostname.

        :param domain: (string) destination hostname
        """
        if domain.startswith("http://"):
            self._fq_domain = domain
        else:
            self._fq_domain = "http://" + domain

        if httpx.head(self._fq_domain).status_code == 200:
            self._session = requests.Session()
        else:
            raise ValueError("cannot connect to host {}".format(self._fq_domain))

    def download_file(self, url, path=None):
        """GETs the resource specified by URL and saves it in the temporary
        files system folder.

        The file operates in binary mode. The user is responsible for file
        resource deallocation.

        :param url: (string) URL to the resource.
        :param path: (string) optional path to file.
        :return: (string) downloaded file path.
        """
        get_url = "{}/{}".format(self._fq_domain, url)
        r = self._session.get(get_url)
        if r.status_code == 200:
            if path:
                save_file(r.content, path)
                return path
            else:
                with NamedTemporaryFile() as ntf:
                    ntf.write(r.content)
                return ntf.name
        else:
            raise ValueError(r.status_code)

    def get(self, url):
        get_url = "{}/{}".format(self._fq_domain, url)
        return self._session.get(get_url)

    def get_json(self, url):
        get_url = "{}/{}".format(self._fq_domain, url)
        r = self._session.get(get_url)
        if r.status_code == 200:
            return json.loads(r.content)
        raise ValueError(r.status_code)

    def post_json(self, url, data):
        """POSTs JSON data to the specified url

        :param url: (string) resource URL to POST.
        :param data: (dict) JSON data in a python dict.
        :return: (requests.Response) server response.
        """
        post_url = "{}/{}".format(self._fq_domain, url)
        return self._session.post(post_url, json=data)

    def post_files(self, url, files):
        post_url = "{}/{}".format(self._fq_domain, url)
        return self._session.post(post_url, files=files)


class AsyncHTTPSessionManager:
    """Utility class for managing a persistent HTTP session."""

    def __init__(self, domain, timeout=None):
        """Initializes the SessionManager to connect to a given hostname.
        A connection timeout can be optionally specified.

        :param domain: (string) destination hostname.
        :param timeout: (int) connection timeout in seconds (defaults=300, or 5 minutes).
        """
        self._timeout = timeout

        if domain.startswith("http://"):
            self._fq_domain = domain
        else:
            self._fq_domain = "http://" + domain

        if not httpx.head(self._fq_domain).status_code == 200:
            raise ValueError("cannot connect to host {}".format(self._fq_domain))

    async def download_file(self, url, path=None):
        """GETs the resource specified by URL and saves it in the temporary
        files system folder.

        The file operates in binary mode. The user is responsible for file
        resource deallocation.

        :param url: (string) URL to the resource.
        :param path: (string) optional path to file.
        :return: (string) path to the downloaded file.
        """
        get_url = "{}/{}".format(self._fq_domain, url)

        async with httpx.AsyncClient() as client:
            r = await client.get(get_url, timeout=self._timeout)

        if r.status_code == 200:
            if path:
                save_file(r.content, path)
                return path
            else:
                with NamedTemporaryFile() as ntf:
                    ntf.write(r.content)
                return ntf.name
        else:
            raise ValueError(r.status_code)

    async def get(self, url):
        get_url = "{}/{}".format(self._fq_domain, url)
        async with httpx.AsyncClient() as client:
            r = await client.get(get_url, timeout=self._timeout)
        return r

    async def get_json(self, url):
        get_url = "{}/{}".format(self._fq_domain, url)
        async with httpx.AsyncClient() as client:
            r = await client.get(get_url, timeout=self._timeout)
        if r.status_code == 200:
            return json.loads(r.content)
        raise ValueError(r.status_code)

    async def post_json(self, url, data):
        """POSTs JSON data to the specified url

        :param url: (string) resource URL to POST.
        :param data: (dict) JSON data in a python dict.
        :return: (requests.Response) server response.
        """
        post_url = "{}/{}".format(self._fq_domain, url)
        async with httpx.AsyncClient() as client:
            r = await client.post(post_url, json=data, timeout=self._timeout)
        return r

    async def post_files(self, url, files):
        post_url = "{}/{}".format(self._fq_domain, url)
        async with httpx.AsyncClient() as client:
            r = await client.post(post_url, files=files, timeout=self._timeout)
        return r


class MockHTTPHandler(SimpleHTTPRequestHandler):
    """Implements a simple HTTP server configurable to serve arbitrary content.

    This class should be considered as a singleton.
    All instances share the same contents.

    Contents can be added via the serve(obj, at) method and removed
    via the clear() method.

    The serve() method supports all objects that can be dumped using
    the json.dumps(obj) function.
    """

    contents = {}

    def do_GET(self):
        if self.path in self.contents:
            self._serve_contents()
        else:
            self._serve_not_found()

    def _serve_contents(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.contents[self.path])

    def _serve_not_found(self):
        self.send_response(404)
        self.end_headers()

    @classmethod
    def clear(cls):
        """Clears the content cache served by the MockHTTPHandler class.

        :return:
        """
        cls.contents = {}

    @classmethod
    def serve(cls, obj, at):
        """Configures this server to serve a specific object at a given URL.
        The object is served in the HTTP response body.

        :param obj: (object) object to serve
        :param at: (string) path URL
        :return: (TestServer) this test server, to enable chain calls.
        """
        json_dump = json.dumps(obj)
        cls.contents[at] = bytes(json_dump, encoding="utf-8")
        return cls


class MockServer:
    """Mock HTTP server. In combination with MockHTTPHandler can be set up to
    serve arbitrary objects for testing purposes.

    Supports objects that can be converted to JSON by the json.dumps() function.

    TODO:
     - implement method POST.
    """

    def __init__(self, handler_class, port=None):
        """Initializes the test server with the handler class.
        A port can be optionally defined for the server to listen on.

        If not specified the port is randomly selected in the range [10000, 20000].

        :param handler_class: (SimpleHTTPRequestHandler) handler for the HTTP requests.
        :param port: (int) port for the server to listen on.
        """
        address = ("localhost", port if port else random.randint(10000, 20000))
        self._server = HTTPServer(address, handler_class)
        self._running = False

    def start(self):
        """Starts the test server.

        :return: None
        """
        if not self._running:
            server_thread = Thread(
                target=self._server.serve_forever,
                name="bad-utils_http-test-server",
                daemon=True,
            )
            server_thread.start()
            self._running = True

    def stop(self):
        """Stops the test server.

        :return: None
        """
        if self._running:
            self._server.shutdown()
            self._running = False
