import counter
from elmpy.testing import sandbox


def test_update_counts() -> None:
    model = counter.update(counter.Model(), counter.ClickedIncrement())
    assert counter.update(model, counter.ClickedIncrement()) == counter.Model(count=2)


def test_clicking_the_buttons() -> None:
    program, page = sandbox(counter.Model(), counter.update, counter.view)

    page.find("button", text="+").click()
    page.find("button", text="+").click()
    page.find("button", text="-").click()

    assert page.text == "-1+"
    assert program.model == counter.Model(count=1)
