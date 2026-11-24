from elmpy.html import (
    Html,
    attribute,
    button,
    class_,
    disabled,
    div,
    input_,
    on_click,
    on_input,
    on_submit,
    p,
    span,
    text,
    value,
)
from elmpy.testing import FakeDocument, FakeElement
from elmpy.vdom import Mounted, Renderer


class Page:
    """Renders views onto a fake page and remembers the messages they send."""

    def __init__(self, html: Html[str]) -> None:
        self.document = FakeDocument()
        self.messages: list[str] = []
        self.renderer = Renderer(self.document, self.messages.append)
        self.mounted: Mounted = self.renderer.create(html)
        self.document.body.appendChild(self.mounted.dom)
        self.document.log.clear()

    @property
    def root(self) -> FakeElement:
        return self.document.body.children[0]

    def patch(self, html: Html[str]) -> list[str]:
        """Patch to `html` and return the DOM changes it made."""
        self.document.log.clear()
        self.mounted = self.renderer.patch(self.mounted, html)
        return self.document.log


def test_create_builds_the_dom() -> None:
    page = Page(div([class_("box"), attribute("title", "Hi")], [span([], [text("hello")])]))

    assert page.root.tagName == "div"
    assert page.root.attributes == {"class": "box", "title": "Hi"}
    assert page.root.text == "hello"


def test_an_unchanged_view_changes_nothing() -> None:
    page = Page(div([class_("box")], [text("hello")]))
    assert page.patch(div([class_("box")], [text("hello")])) == []


def test_changed_text_is_the_only_change() -> None:
    page = Page(div([], [span([], [text("0")]), button([on_click("+")], [text("+")])]))
    root = page.root

    assert page.patch(div([], [span([], [text("1")]), button([on_click("+")], [text("+")])])) == [
        "set text '1'"
    ]
    assert page.root is root  # the same DOM node, updated in place


def test_a_different_tag_replaces_the_node() -> None:
    page = Page(div([], [span([], [text("a")])]))
    old_span = page.root.children[0]

    page.patch(div([], [p([], [text("a")])]))

    assert page.root.children[0].tagName == "p"
    assert old_span.parentNode is None


def test_children_are_added_and_removed_at_the_end() -> None:
    page = Page(div([], [text("a")]))

    assert page.patch(div([], [text("a"), text("b")])) == [
        "createTextNode 'b'",
        "appendChild <div>",
    ]
    assert page.patch(div([], [text("a")])) == ["removeChild <div>"]
    assert page.root.text == "a"


def test_boolean_and_removed_attributes() -> None:
    page = Page(button([disabled(True), class_("big")], []))
    assert page.root.attributes == {"disabled": "", "class": "big"}

    page.patch(button([disabled(False)], []))

    assert page.root.attributes == {}


def test_value_is_a_property_and_is_not_reset_while_typing() -> None:
    page = Page(input_([value("a"), on_input(lambda typed: typed)]))
    assert page.root.value == "a"

    page.root.type("ab")
    assert page.messages == ["ab"]
    assert page.patch(input_([value("ab"), on_input(lambda typed: typed)])) == []

    page.patch(input_([]))
    assert page.root.value == ""


def test_new_handlers_reuse_the_existing_listener() -> None:
    page = Page(button([on_click("first")], []))

    assert page.patch(button([on_click("second")], [])) == []
    page.root.click()

    assert page.messages == ["second"]


def test_listeners_are_removed_with_their_handler_or_node() -> None:
    page = Page(div([], [button([on_click("a")], [])]))
    clicked = page.root.children[0]

    assert page.patch(div([], [button([], [])])) == ["removeEventListener click"]

    page.patch(div([], [button([on_click("a")], [])]))
    assert page.patch(div([], [])) == ["removeChild <div>", "removeEventListener click"]
    assert clicked.listeners == {"click": []}


def test_submit_prevents_the_page_reload() -> None:
    page = Page(div([], []))
    page.patch(div([], [p([on_submit("sent")], [])]))

    page.root.children[0].submit()  # fails if preventDefault was not called

    assert page.messages == ["sent"]
