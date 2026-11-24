"""Run an elmpy program in pytest, against a small fake DOM instead of a browser.

    program, page = sandbox(counter.Model(), counter.update, counter.view)
    page.find("button", text="+").click()
    assert page.text == "-1+"

The fake DOM implements only what `elmpy.vdom` uses, plus a few helpers for
tests (`find`, `click`, `type`, `toggle`, `submit`). Every change the renderer
makes is recorded in `FakeDocument.log`, so tests can check that a patch did
as little work as possible.
"""

from collections.abc import Callable

from .html import Html
from .runtime import Program

type EventListener = Callable[[FakeEvent], None]


class FakeDocument:
    def __init__(self) -> None:
        self.log: list[str] = []
        self.body = FakeElement(self, "body")

    def createElement(self, tag: str) -> FakeElement:
        self.log.append(f"createElement {tag}")
        return FakeElement(self, tag)

    def createTextNode(self, content: str) -> FakeText:
        self.log.append(f"createTextNode {content!r}")
        return FakeText(self, content)


class FakeEvent:
    def __init__(self, event_type: str, current_target: FakeElement) -> None:
        self.type = event_type
        self.currentTarget = current_target
        self.default_prevented = False

    def preventDefault(self) -> None:
        self.default_prevented = True


class FakeNode:
    def __init__(self, document: FakeDocument) -> None:
        self.ownerDocument = document
        self.parentNode: FakeElement | None = None

    @property
    def text(self) -> str:
        """All the text inside this node, like the DOM's `textContent`."""
        raise NotImplementedError


class FakeText(FakeNode):
    def __init__(self, document: FakeDocument, content: str) -> None:
        super().__init__(document)
        self._content = content

    @property
    def nodeValue(self) -> str:
        return self._content

    @nodeValue.setter
    def nodeValue(self, content: str) -> None:
        self.ownerDocument.log.append(f"set text {content!r}")
        self._content = content

    @property
    def text(self) -> str:
        return self._content


class FakeElement(FakeNode):
    def __init__(self, document: FakeDocument, tag: str) -> None:
        super().__init__(document)
        self.tagName = tag
        self.attributes: dict[str, str] = {}
        self.childNodes: list[FakeNode] = []
        self.listeners: dict[str, list[EventListener]] = {}
        self._value = ""
        self._checked = False

    # --- The DOM methods and properties that elmpy.vdom uses ---------------

    def appendChild(self, child: FakeNode) -> None:
        self._log(f"appendChild <{self.tagName}>")
        child.parentNode = self
        self.childNodes.append(child)

    def removeChild(self, child: FakeNode) -> None:
        self._log(f"removeChild <{self.tagName}>")
        child.parentNode = None
        self.childNodes.remove(child)

    def replaceChild(self, new: FakeNode, old: FakeNode) -> None:
        self._log(f"replaceChild <{self.tagName}>")
        self.childNodes[self.childNodes.index(old)] = new
        new.parentNode, old.parentNode = self, None

    def setAttribute(self, name: str, value: str) -> None:
        self._log(f"setAttribute {name}={value!r}")
        self.attributes[name] = value

    def removeAttribute(self, name: str) -> None:
        self._log(f"removeAttribute {name}")
        self.attributes.pop(name, None)

    def addEventListener(self, event: str, listener: EventListener) -> None:
        self._log(f"addEventListener {event}")
        self.listeners.setdefault(event, []).append(listener)

    def removeEventListener(self, event: str, listener: EventListener) -> None:
        self._log(f"removeEventListener {event}")
        self.listeners[event].remove(listener)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._log(f"set value {value!r}")
        self._value = value

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, checked: bool) -> None:
        self._log(f"set checked {checked}")
        self._checked = checked

    # --- Helpers for tests --------------------------------------------------

    @property
    def text(self) -> str:
        return "".join(child.text for child in self.childNodes)

    @property
    def children(self) -> list[FakeElement]:
        """Child elements, skipping text nodes."""
        return [child for child in self.childNodes if isinstance(child, FakeElement)]

    def find_all(self, tag: str, text: str | None = None) -> list[FakeElement]:
        """Every element inside this one with this tag (and this exact text, if given)."""
        found: list[FakeElement] = []
        for child in self.children:
            if child.tagName == tag and (text is None or child.text == text):
                found.append(child)
            found.extend(child.find_all(tag, text))
        return found

    def find(self, tag: str, text: str | None = None) -> FakeElement:
        """The first matching element. Fails the test if there is none."""
        found = self.find_all(tag, text)
        assert found, f"no <{tag}> with text {text!r} inside <{self.tagName}>"
        return found[0]

    def dispatch_event(self, event_type: str) -> FakeEvent:
        event = FakeEvent(event_type, self)
        for listener in list(self.listeners.get(event_type, [])):
            listener(event)
        return event

    def click(self) -> None:
        self.dispatch_event("click")

    def type(self, value: str) -> None:
        """Replace the input's text, as if the user typed it."""
        self._value = value
        self.dispatch_event("input")

    def toggle(self) -> None:
        """Flip a checkbox, as if the user clicked it."""
        self._checked = not self._checked
        self.dispatch_event("change")

    def submit(self) -> None:
        event = self.dispatch_event("submit")
        assert event.default_prevented, "the browser would reload the page; use on_submit"

    def _log(self, entry: str) -> None:
        self.ownerDocument.log.append(entry)


def sandbox[Model, Message](
    init: Model,
    update: Callable[[Model, Message], Model],
    view: Callable[[Model], Html[Message]],
) -> tuple[Program[Model, Message], FakeElement]:
    """Like `elmpy.browser.sandbox`, but on a fake page. Returns the program and the page."""
    page = FakeDocument().body
    return Program(init, update, view, page), page
