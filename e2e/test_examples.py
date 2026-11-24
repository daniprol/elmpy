"""The examples, running in a real browser on Pyodide."""

from playwright.sync_api import Page, expect

PYODIDE_TIMEOUT_MS = 60_000  # the first load downloads Pyodide (about 10 MB)


def test_counter(app: Page) -> None:
    app.goto("/examples/counter/")
    counter = app.locator(".counter")
    expect(counter).to_have_text("-0+", timeout=PYODIDE_TIMEOUT_MS)

    app.get_by_role("button", name="+").click()
    app.get_by_role("button", name="+").click()
    app.get_by_role("button", name="-").click()

    expect(counter).to_have_text("-1+")


def test_todo(app: Page) -> None:
    app.goto("/examples/todo/")
    draft = app.get_by_placeholder("What needs doing?")
    expect(draft).to_be_visible(timeout=PYODIDE_TIMEOUT_MS)
    expect(draft).to_be_focused()

    draft.fill("Buy milk")
    draft.press("Enter")  # submits the form without reloading the page
    draft.press_sequentially("Walk dog")
    app.get_by_role("button", name="Add").click()

    items = app.locator("li")
    expect(items).to_have_text(["Buy milkDelete", "Walk dogDelete"])
    expect(draft).to_have_value("")

    items.first.get_by_role("checkbox").check()
    expect(items.first).to_have_class("done")
    expect(app.get_by_text("1 left")).to_be_visible()

    items.first.get_by_role("button", name="Delete").click()
    expect(items).to_have_text(["Walk dogDelete"])
    expect(items.first.get_by_role("checkbox")).not_to_be_checked()
