"""HTTP page for setting learning-job parameters and reading results."""

from __future__ import annotations

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ml_studio.catalog import catalog
from ml_studio.runner import TaskRunner

_log = logging.getLogger(__name__)
_STATIC_DIR = Path(__file__).resolve().parent / "static"
_MAX_BODY = 65_536
_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


def make_server(
    host: str, port: int, runner: TaskRunner
) -> ThreadingHTTPServer:
    """Build a threaded server that serves the page and the job API."""

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
            self._route("GET")

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
            self._route("POST")

        def log_message(self, fmt: str, *args: Any) -> None:
            _log.info("%s - " + fmt, self.address_string(), *args)

        def _route(self, method: str) -> None:
            path = urlparse(self.path).path
            if method == "GET" and path == "/":
                self._file(_STATIC_DIR / "index.html")
                return
            if method == "GET" and path.startswith("/static/"):
                self._static(path.removeprefix("/static/"))
                return
            if method == "GET" and path == "/api/catalog":
                self._json(200, catalog())
                return
            if method == "GET" and path == "/api/jobs":
                self._json(200, {"jobs": runner.list_jobs()})
                return
            job_id, rest = _job_path(path)
            if job_id is None:
                self._error(404, "That page is not part of the learning bench.")
                return
            try:
                if method == "GET" and rest == "":
                    self._json(200, runner.get(job_id))
                    return
                if method == "POST" and rest == "/cancel":
                    self._json(200, runner.cancel(job_id))
                    return
                figure = _figure_name(rest)
                if method == "GET" and figure is not None:
                    self._png(runner.figure(job_id, figure))
                    return
            except KeyError:
                self._error(404, "That job or figure is not available.")
                return
            self._error(404, "That page is not part of the learning bench.")

        def _read_json(self) -> dict[str, Any] | None:
            try:
                length = int(self.headers.get("Content-Length", "0") or 0)
            except ValueError:
                self._error(400, "Content-Length must be an integer.")
                return None
            if length < 0 or length > _MAX_BODY:
                self._error(413, "Request body is too large.")
                return None
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._error(400, "Body must be JSON.")
                return None
            if not isinstance(payload, dict):
                self._error(400, "Body must be a JSON object.")
                return None
            return payload

        def _static(self, name: str) -> None:
            root = _STATIC_DIR.resolve()
            candidate = (root / name).resolve()
            escaped = not candidate.is_relative_to(root)
            if escaped or candidate.suffix not in _CONTENT_TYPES:
                self._error(404, "That file is not available.")
                return
            self._file(candidate)

        def _file(self, path: Path) -> None:
            if not path.is_file():
                self._error(404, "That file is not available.")
                return
            content_type = _CONTENT_TYPES.get(path.suffix, "application/octet-stream")
            self._send(200, path.read_bytes(), content_type)

        def _png(self, payload: bytes) -> None:
            self._send(200, payload, "image/png")

        def _json(self, status: int, payload: Any) -> None:
            body = json.dumps(payload).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8")

        def _error(self, status: int, message: str) -> None:
            self._json(status, {"error": message})

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    def _post_jobs(handler: Handler) -> None:
        payload = handler._read_json()
        if payload is None:
            return
        try:
            job_id = runner.submit(payload)
        except ValueError as exc:
            handler._error(400, str(exc))
            return
        except RuntimeError as exc:
            handler._error(429, str(exc))
            return
        handler._json(202, runner.get(job_id))

    original_route = Handler._route

    def route_with_post(self: Handler, method: str) -> None:
        if method == "POST" and urlparse(self.path).path == "/api/jobs":
            _post_jobs(self)
            return
        original_route(self, method)

    Handler._route = route_with_post  # type: ignore[method-assign]
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.daemon_threads = True
    return httpd


def serve(
    host: str = "127.0.0.1",
    port: int = 47321,
    *,
    max_workers: int = 2,
    runner: TaskRunner | None = None,
) -> None:
    """
    Serve the parameter page until the process is stopped.

    Parameters
    ----------
    host, port : str, int
        Address to bind. The default is local-only, port 47321.
    max_workers : int
        How many fits may run at once. From 1 to 4.
    runner : TaskRunner, optional
        Runner to use. A new one is created when omitted.
    """
    owned = runner is None
    if runner is None:
        runner = TaskRunner(max_workers=max_workers)
    httpd = make_server(host, port, runner)
    _log.info("Learning bench at http://%s:%s", host, port)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
        if owned:
            runner.shutdown(wait=False)


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and serve the learning bench."""
    parser = argparse.ArgumentParser(
        description="Fit scikit-learn models and plot them with Matplotlib."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=47321)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    serve(args.host, args.port, max_workers=args.workers)


def _job_path(path: str) -> tuple[str | None, str]:
    prefix = "/api/jobs/"
    if not path.startswith(prefix):
        return None, ""
    rest = path.removeprefix(prefix)
    job_id, separator, tail = rest.partition("/")
    hex_digits = "0123456789abcdef"
    if len(job_id) != 12 or any(character not in hex_digits for character in job_id):
        return None, ""
    return job_id, f"/{tail}" if separator else ""


def _figure_name(rest: str) -> str | None:
    prefix = "/figures/"
    suffix = ".png"
    if not (rest.startswith(prefix) and rest.endswith(suffix)):
        return None
    name = rest[len(prefix) : -len(suffix)]
    letters = "abcdefghijklmnopqrstuvwxyz_"
    if not name or any(character not in letters for character in name):
        return None
    return name
