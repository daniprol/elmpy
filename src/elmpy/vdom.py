"""Turn `Html` values into DOM nodes, and update those nodes when the view changes.

This is the "virtual DOM diff". After each update the runtime calls `patch` with
the new view. `patch` compares it with the previous one and changes only the DOM
nodes that differ, so typing in an input or clicking a button never rebuilds
the whole page.

This module never imports `js`. It talks to whatever `document` it is given: the
real one in the browser, or `elmpy.testing.FakeDocument` in pytest.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import partial
from typing import Any

from .html import Attribute, Element, Event, EventHandler, Html, HtmlAttribute, Text

type DomNode = Any
"""A DOM node: a JavaScript object in the browser, a fake one in tests."""

type Listener = Any
"""What `addEventListener` receives: a Pyodide proxy in the browser."""

PROPERTY_DEFAULTS: dict[str, str | bool] = {"value": "", "checked": False}
"""Attributes that hold live state, so we set them as DOM properties instead.

`setAttribute("value", ...)` only sets an input's *initial* text. Once the user
types, only the `value` property shows what is in the box. The dict value is
what the property goes back to when the attribute is removed from the view.
"""


@dataclass
class Mounted:
    """A piece of the view that is on the page: the `Html` and its DOM node."""

    html: Html[Any]
    dom: DomNode
    children: list[Mounted] = field(default_factory=lambda: [])
    listeners: dict[str, Listener] = field(default_factory=lambda: {})


class Renderer:
    def __init__(
        self,
        document: DomNode,
        dispatch: Callable[[Any], None],
        make_listener: Callable[[Callable[[Any], None]], Listener] = lambda function: function,
    ) -> None:
        self.document = document
        self.dispatch = dispatch
        # In the browser this is `pyodide.ffi.create_proxy`: it keeps a Python
        # function alive while JavaScript holds on to it as an event listener.
        self.make_listener = make_listener

    def create(self, html: Html[Any]) -> Mounted:
        """Build brand-new DOM nodes for `html`."""
        match html:
            case Text(content):
                return Mounted(html, self.document.createTextNode(content))
            case Element(tag, attributes, children):
                mounted = Mounted(html, self.document.createElement(tag))
                self._update_attributes(mounted, (), attributes)
                for child in children:
                    self._append_child(mounted, child)
                return mounted

    def patch(self, old: Mounted, new: Html[Any]) -> Mounted:
        """Change the DOM of `old` so that it shows `new`. Returns what is mounted now."""
        if old.html is new:  # nothing changed: same object, same DOM
            return old

        match old.html, new:
            case Text(old_content), Text(new_content):
                if old_content != new_content:
                    old.dom.nodeValue = new_content
            case Element() as old_element, Element() as new_element if (
                old_element.tag == new_element.tag
            ):
                self._update_attributes(old, old_element.attributes, new_element.attributes)
                self._patch_children(old, new_element.children)
            case _:  # a different kind of node: build a new one and swap it in
                fresh = self.create(new)
                old.dom.parentNode.replaceChild(fresh.dom, old.dom)
                self.destroy(old)
                return fresh

        old.html = new  # event handlers read the newest view from here
        return old

    def destroy(self, mounted: Mounted) -> None:
        """Release the event listeners of a node that left the page, and of its children."""
        for event, listener in mounted.listeners.items():
            mounted.dom.removeEventListener(event, listener)
            _release(listener)
        for child in mounted.children:
            self.destroy(child)

    def _append_child(self, parent: Mounted, html: Html[Any]) -> None:
        child = self.create(html)
        parent.dom.appendChild(child.dom)
        parent.children.append(child)

    def _patch_children(self, parent: Mounted, new_children: Sequence[Html[Any]]) -> None:
        """Match old and new children by position: first with first, second with second."""
        old_children = parent.children
        parent.children = [
            self.patch(old, new) for old, new in zip(old_children, new_children, strict=False)
        ]
        for new in new_children[len(old_children) :]:
            self._append_child(parent, new)
        for gone in old_children[len(new_children) :]:
            parent.dom.removeChild(gone.dom)
            self.destroy(gone)

    def _update_attributes(
        self,
        mounted: Mounted,
        old: Sequence[Attribute[Any]],
        new: Sequence[Attribute[Any]],
    ) -> None:
        old_values = _attribute_values(old)
        new_values = _attribute_values(new)
        for name in old_values.keys() - new_values.keys():
            _remove_attribute(mounted.dom, name)
        for name, value in new_values.items():
            # Properties are compared with the live DOM, which the user may have changed.
            if name in PROPERTY_DEFAULTS or old_values.get(name) != value:
                _set_attribute(mounted.dom, name, value)
        self._update_listeners(mounted, new)

    def _update_listeners(self, mounted: Mounted, attributes: Sequence[Attribute[Any]]) -> None:
        """Keep exactly one DOM listener per event name the element handles.

        The listener does not hold the handler itself. It looks the handler up in
        `mounted.html` when the event fires, so a new view never needs a new listener.
        """
        events = {handler.event for handler in attributes if isinstance(handler, EventHandler)}
        for event in mounted.listeners.keys() - events:
            listener = mounted.listeners.pop(event)
            mounted.dom.removeEventListener(event, listener)
            _release(listener)
        for event in events - mounted.listeners.keys():
            listener = self.make_listener(partial(self._handle_event, mounted))
            mounted.dom.addEventListener(event, listener)
            mounted.listeners[event] = listener

    def _handle_event(self, mounted: Mounted, dom_event: Any) -> None:
        assert isinstance(mounted.html, Element)
        for handler in mounted.html.attributes:
            if isinstance(handler, EventHandler) and handler.event == dom_event.type:
                if handler.prevent_default:
                    dom_event.preventDefault()
                message = handler.to_message(_read_event(dom_event))
                if message is not None:
                    self.dispatch(message)


def _attribute_values(attributes: Sequence[Attribute[Any]]) -> dict[str, str | bool]:
    return {item.name: item.value for item in attributes if isinstance(item, HtmlAttribute)}


def _set_attribute(dom: DomNode, name: str, value: str | bool) -> None:
    if name in PROPERTY_DEFAULTS:
        # Setting `value` to what it already is would move the cursor while typing.
        if getattr(dom, name) != value:
            setattr(dom, name, value)
    elif value is True:
        dom.setAttribute(name, "")
    elif value is False:
        dom.removeAttribute(name)
    else:
        dom.setAttribute(name, value)


def _remove_attribute(dom: DomNode, name: str) -> None:
    if name in PROPERTY_DEFAULTS:
        setattr(dom, name, PROPERTY_DEFAULTS[name])
    else:
        dom.removeAttribute(name)


def _read_event(dom_event: Any) -> Event:
    """Copy what handlers need out of the DOM event, so user code never sees JavaScript."""
    # `currentTarget` is the element with the listener. `target` could be a child
    # of it, like a <span> inside the <button> that was clicked.
    element = dom_event.currentTarget
    return Event(
        type=str(dom_event.type),
        value=str(getattr(element, "value", "") or ""),
        checked=bool(getattr(element, "checked", False)),
    )


def _release(listener: Listener) -> None:
    """Free a Pyodide proxy. Plain Python functions (used in tests) have nothing to free."""
    destroy = getattr(listener, "destroy", None)
    if destroy is not None:
        destroy()
