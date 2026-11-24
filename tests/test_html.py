from elmpy.html import (
    Element,
    Event,
    EventHandler,
    Text,
    class_,
    div,
    input_,
    map_html,
    on_check,
    on_click,
    on_input,
    text,
)


def test_views_are_plain_comparable_data() -> None:
    assert div([class_("box")], [text("hi")]) == div([class_("box")], [text("hi")])
    assert div([], [text("hi")]) != div([], [text("bye")])


def test_on_input_reads_the_value() -> None:
    handler = on_input(lambda value: f"typed {value}")
    assert handler.to_message(Event("input", value="abc")) == "typed abc"


def test_on_check_reads_checked() -> None:
    handler = on_check(lambda done: done)
    assert handler.to_message(Event("change", checked=True)) is True


def test_map_html_wraps_every_message_and_keeps_the_rest() -> None:
    child = div([class_("child")], [text("x"), input_([on_click("clicked")])])

    mapped = map_html(lambda message: ("child", message), child)

    assert isinstance(mapped, Element)
    assert mapped.attributes == (class_("child"),)
    assert mapped.children[0] == Text("x")
    field = mapped.children[1]
    assert isinstance(field, Element)
    handler = field.attributes[0]
    assert isinstance(handler, EventHandler)
    assert handler.to_message(Event("click")) == ("child", "clicked")
