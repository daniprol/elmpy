"""Build views as plain Python data.

A view is a tree of `Element` and `Text` values. Each tag function takes a list
of attributes and a list of children, like Foldkit and Elm:

    div([class_("counter")], [
        button([on_click(ClickedIncrement())], [text("+")]),
    ])

Nothing here touches the browser. `elmpy.vdom` turns this data into DOM nodes.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Generic, Never

from ._message import Message

# --- The data a view is made of ---------------------------------------------


@dataclass(frozen=True, slots=True)
class Event:
    """The parts of a DOM event that a handler may read. The runtime fills it in."""

    type: str
    value: str = ""
    checked: bool = False


@dataclass(frozen=True, slots=True)
class HtmlAttribute:
    """A plain attribute such as `class="todo"`. `True`/`False` add or remove it."""

    name: str
    value: str | bool


@dataclass(frozen=True, slots=True)
class EventHandler(Generic[Message]):  # noqa: UP046 (see _message.py)
    """Turns a DOM event into a message, or into `None` to ignore the event."""

    event: str
    to_message: Callable[[Event], Message | None]
    prevent_default: bool = False


type Attribute[Message] = HtmlAttribute | EventHandler[Message]


@dataclass(frozen=True, slots=True)
class Text:
    """A text node."""

    text: str


@dataclass(frozen=True, slots=True)
class Element(Generic[Message]):  # noqa: UP046 (see _message.py)
    """An HTML element with its attributes and children."""

    tag: str
    attributes: tuple[Attribute[Message], ...]
    children: tuple[Html[Message], ...]


type Html[Message] = Element[Message] | Text
"""Anything a view can return. `Html[Message]` can only produce `Message`s."""


# --- Elements -------------------------------------------------------------
# `[Message = Never]`: an element without event handlers can't produce any
# message, so its type is `Element[Never]`, which fits into any view.


def element[Message = Never](
    tag: str,
    attributes: Sequence[Attribute[Message]],
    children: Sequence[Html[Message]],
) -> Element[Message]:
    """Any element. The tag functions below are shortcuts for this."""
    return Element(tag, tuple(attributes), tuple(children))


def text(content: str) -> Text:
    return Text(content)


def a[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("a", attributes, children)


def button[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("button", attributes, children)


def div[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("div", attributes, children)


def footer[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("footer", attributes, children)


def form[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("form", attributes, children)


def h1[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("h1", attributes, children)


def h2[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("h2", attributes, children)


def header[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("header", attributes, children)


def input_[Message = Never](attributes: Sequence[Attribute[Message]]) -> Element[Message]:
    """`<input>` never has children, so it only takes attributes."""
    return element("input", attributes, [])


def label[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("label", attributes, children)


def li[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("li", attributes, children)


def main[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("main", attributes, children)


def p[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("p", attributes, children)


def section[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("section", attributes, children)


def span[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("span", attributes, children)


def ul[Message = Never](
    attributes: Sequence[Attribute[Message]], children: Sequence[Html[Message]]
) -> Element[Message]:
    return element("ul", attributes, children)


# --- Attributes -----------------------------------------------------------
# Names that clash with Python keywords or builtins get a trailing underscore.


def attribute(name: str, value: str | bool) -> HtmlAttribute:
    """Any attribute. The functions below are shortcuts for this."""
    return HtmlAttribute(name, value)


def autofocus(flag: bool) -> HtmlAttribute:
    return HtmlAttribute("autofocus", flag)


def checked(flag: bool) -> HtmlAttribute:
    return HtmlAttribute("checked", flag)


def class_(name: str) -> HtmlAttribute:
    return HtmlAttribute("class", name)


def disabled(flag: bool) -> HtmlAttribute:
    return HtmlAttribute("disabled", flag)


def for_(element_id: str) -> HtmlAttribute:
    return HtmlAttribute("for", element_id)


def href(url: str) -> HtmlAttribute:
    return HtmlAttribute("href", url)


def id_(element_id: str) -> HtmlAttribute:
    return HtmlAttribute("id", element_id)


def placeholder(content: str) -> HtmlAttribute:
    return HtmlAttribute("placeholder", content)


def type_(input_type: str) -> HtmlAttribute:
    return HtmlAttribute("type", input_type)


def value(content: str) -> HtmlAttribute:
    return HtmlAttribute("value", content)


# --- Events ---------------------------------------------------------------


def on[Message](
    event: str,
    to_message: Callable[[Event], Message | None],
    *,
    prevent_default: bool = False,
) -> EventHandler[Message]:
    """Listen to any DOM event. The functions below are shortcuts for this."""
    return EventHandler(event, to_message, prevent_default)


def on_click[Message](message: Message) -> EventHandler[Message]:
    return EventHandler("click", lambda _event: message)


def on_input[Message](to_message: Callable[[str], Message]) -> EventHandler[Message]:
    """Called with the input's new text on every keystroke."""
    return EventHandler("input", lambda event: to_message(event.value))


def on_check[Message](to_message: Callable[[bool], Message]) -> EventHandler[Message]:
    """Called with the checkbox's new state."""
    return EventHandler("change", lambda event: to_message(event.checked))


def on_submit[Message](message: Message) -> EventHandler[Message]:
    """Stops the browser from reloading the page, which would also stop Python."""
    return EventHandler("submit", lambda _event: message, prevent_default=True)


# --- Embedding a child view -----------------------------------------------


def map_html[Message, ParentMessage](
    wrap: Callable[[Message], ParentMessage],
    html: Html[Message],
) -> Html[ParentMessage]:
    """Wrap every message a child view produces, so the parent can tell it apart.

    `map_html(GotCounter, counter.view(model.counter))` turns each
    `counter.Message` into `GotCounter(message)`.
    """
    match html:
        case Text():
            return html
        case Element(tag, attributes, children):
            return Element(
                tag,
                tuple(_map_attribute(wrap, attribute) for attribute in attributes),
                tuple(map_html(wrap, child) for child in children),
            )


def _map_attribute[Message, ParentMessage](
    wrap: Callable[[Message], ParentMessage],
    attribute: Attribute[Message],
) -> Attribute[ParentMessage]:
    match attribute:
        case HtmlAttribute():
            return attribute
        case EventHandler(event, to_message, prevent_default):

            def to_parent_message(event_data: Event) -> ParentMessage | None:
                message = to_message(event_data)
                return None if message is None else wrap(message)

            return EventHandler(event, to_parent_message, prevent_default)
