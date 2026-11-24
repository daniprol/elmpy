from elmpy.html import Html, button, on_click, text
from elmpy.runtime import Program
from elmpy.testing import FakeDocument


def view(model: int) -> Html[str]:
    return button([on_click("clicked")], [text(str(model))])


def test_dispatch_updates_the_model_and_the_page() -> None:
    page = FakeDocument().body
    program = Program(0, lambda model, _message: model + 1, view, page)

    program.dispatch("clicked")
    page.find("button").click()

    assert program.model == 2
    assert page.text == "2"


def test_a_message_sent_during_update_waits_for_its_turn() -> None:
    handled: list[str] = []

    def update(model: int, message: str) -> int:
        handled.append(f"start {message}")
        if message == "first":
            program.dispatch("second")  # must not run inside this update
        handled.append(f"end {message}")
        return model + 1

    program = Program(0, update, view, FakeDocument().body)
    program.dispatch("first")

    assert handled == ["start first", "end first", "start second", "end second"]
    assert program.model == 2
