"""A counter: the "hello world" of the Elm Architecture."""

from dataclasses import dataclass, replace
from typing import assert_never

from elmpy.html import Html, button, class_, div, on_click, span, text

# --- Model: everything the app knows ---------------------------------------


@dataclass(frozen=True)
class Model:
    count: int = 0


# --- Messages: everything that can happen ----------------------------------


@dataclass(frozen=True)
class ClickedIncrement: ...


@dataclass(frozen=True)
class ClickedDecrement: ...


type Message = ClickedIncrement | ClickedDecrement


# --- Update: how each message changes the model ----------------------------


def update(model: Model, message: Message) -> Model:
    match message:
        case ClickedIncrement():
            return replace(model, count=model.count + 1)
        case ClickedDecrement():
            return replace(model, count=model.count - 1)
        case _:
            assert_never(message)


# --- View: what the model looks like on the page ---------------------------


def view(model: Model) -> Html[Message]:
    return div(
        [class_("counter")],
        [
            button([on_click(ClickedDecrement())], [text("-")]),
            span([], [text(str(model.count))]),
            button([on_click(ClickedIncrement())], [text("+")]),
        ],
    )
