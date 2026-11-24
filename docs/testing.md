# Testing

## Test `update` directly

`update` is a pure function, so a test is one call and one comparison.

## Test the page without a browser

`elmpy.testing.sandbox` runs your app against a small fake DOM. You can click,
type, toggle and submit, then check the text on the page and the model.
Both kinds of test, for the counter:

```python title="test_counter.py"
--8<-- "examples/counter/test_counter.py"
```

The fake page has `find`, `find_all`, `click`, `type`, `toggle` and `submit`.
See [`test_todo.py`](examples.md#todo-list) for a longer example.

## Check what the diff did

Every DOM change is recorded in `FakeDocument.log`. Use it to check that a patch did
only what it should:

```python
program, page = sandbox(counter.Model(), counter.update, counter.view)
page.ownerDocument.log.clear()

page.find("button", text="+").click()

assert page.ownerDocument.log == ["set text '1'"]
```

## In a real browser

The repository also runs each example in Chromium with Playwright
(`uv run pytest e2e`). Those tests check that the app loads on Pyodide and that the
main clicks work. Keep detailed checks in the fast tests above.
