"""Serve the repository over HTTP so the browser can load the examples."""

import functools
import threading
from collections.abc import Iterator
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import ConsoleMessage, Page

REPOSITORY = Path(__file__).parent.parent


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Overrides pytest-playwright's `base_url`, so `page.goto("/examples/...")` works."""
    handler = functools.partial(QuietHandler, directory=REPOSITORY)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def app(page: Page) -> Iterator[Page]:
    """A page that fails the test if Python or JavaScript logs an error."""
    errors: list[str] = []

    def on_console(message: ConsoleMessage) -> None:
        if message.type == "error":
            errors.append(message.text)

    page.on("console", on_console)
    page.on("pageerror", lambda error: errors.append(str(error)))
    yield page
    assert errors == []
