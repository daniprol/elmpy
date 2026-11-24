"""Checks for the type checker, not for pytest.

Each line marked `# pyright: ignore[...]` is a mistake that pyright must catch.
Because `reportUnnecessaryTypeIgnoreComment` is on, pyright fails if one of these
lines ever stops being an error. The unmarked code must keep passing.
"""

from dataclasses import dataclass

from elmpy.html import Html, button, div, map_html, on_click, on_input, span, text


@dataclass(frozen=True)
class ChildClicked: ...


@dataclass(frozen=True)
class GotChild:
    message: ChildClicked


@dataclass(frozen=True)
class ParentClicked: ...


type ParentMessage = GotChild | ParentClicked


def child_view() -> Html[ChildClicked]:
    return button([on_click(ChildClicked())], [text("child")])


# --- Must pass --------------------------------------------------------------


def parent_view() -> Html[ParentMessage]:
    return div([], [map_html(GotChild, child_view()), button([on_click(ParentClicked())], [])])


def view_with_local_variable() -> Html[ParentMessage]:
    # A view of one message type fits where a wider message type is expected.
    clicked = button([on_click(ParentClicked())], [text("ok")])
    return div([], [clicked])


def view_without_handlers() -> Html[ParentMessage]:
    # Elements without handlers are `Element[Never]`, so they fit in any view.
    return div([], [span([], [text("static")])])


# --- Must fail --------------------------------------------------------------


def forgot_map_html() -> Html[ParentMessage]:
    return div([], [child_view()])  # pyright: ignore[reportReturnType]


def forgot_map_html_on_second_child() -> Html[ParentMessage]:
    return div([], [map_html(GotChild, child_view()), child_view()])  # pyright: ignore[reportReturnType]


def wrong_message_in_handler() -> Html[ChildClicked]:
    return button([on_click(ParentClicked())], [])  # pyright: ignore[reportReturnType]


def handler_returns_wrong_type() -> Html[ChildClicked]:
    return span([on_input(lambda text: text)], [])  # pyright: ignore[reportReturnType]
