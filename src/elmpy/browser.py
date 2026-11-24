"""Start an elmpy program on a real web page.

This is the only module that imports `js` and `pyodide`, which exist only inside
the browser. Keeping them here lets everything else run in plain pytest.
"""

from collections.abc import Callable

import js  # pyright: ignore[reportMissingModuleSource] (only exists inside Pyodide)
from pyodide.ffi import create_proxy

from .html import Html
from .runtime import Program


def sandbox[Model, Message](
    init: Model,
    update: Callable[[Model, Message], Model],
    view: Callable[[Model], Html[Message]],
    mount: str = "#app",
) -> Program[Model, Message]:
    """Show the app inside the element that matches the CSS selector `mount`."""
    container = js.document.querySelector(mount)
    if container is None:
        raise ValueError(f"No element on the page matches {mount!r}")
    container.replaceChildren()  # remove the "Loading…" placeholder
    return Program(init, update, view, container, make_listener=create_proxy)
