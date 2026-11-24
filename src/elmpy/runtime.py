"""The loop at the heart of the Elm Architecture.

message ──> update(model, message) ──> new model ──> view(model) ──> patch the DOM
   ^                                                                       │
   └──────────────────── the user clicks or types ─────────────────────────┘
"""

from collections import deque
from collections.abc import Callable
from typing import Any

from .html import Html
from .vdom import DomNode, Listener, Renderer


class Program[Model, Message]:
    """Runs one app: holds the model, applies each message, and keeps the page up to date."""

    def __init__(
        self,
        init: Model,
        update: Callable[[Model, Message], Model],
        view: Callable[[Model], Html[Message]],
        container: DomNode,
        make_listener: Callable[[Callable[[Any], None]], Listener] = lambda function: function,
    ) -> None:
        self.model = init
        self.update = update
        self.view = view
        self.container = container
        self._queue: deque[Message] = deque()
        self._busy = False
        self._renderer = Renderer(container.ownerDocument, self.dispatch, make_listener)
        self._mounted = self._renderer.create(view(init))
        container.appendChild(self._mounted.dom)

    def dispatch(self, message: Message) -> None:
        """Apply `message` and re-render. Event handlers call this for you."""
        self._queue.append(message)
        if self._busy:
            # A message sent while we are still updating or patching (for example a
            # `blur` fired by removing a focused input) waits for its turn.
            return
        self._busy = True
        try:
            while self._queue:
                self.model = self.update(self.model, self._queue.popleft())
                self._mounted = self._renderer.patch(self._mounted, self.view(self.model))
        finally:
            self._busy = False
