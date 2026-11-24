# Get started

## Run the examples

You need [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/daniprol/elmpy
cd elmpy
uv sync
uv run python -m http.server
```

Open <http://localhost:8000/examples/counter/>. The first load takes a few seconds
while the browser downloads Pyodide.

## Your first app

An app is a Python module with four parts. Here is the whole counter:

```python title="counter.py"
--8<-- "examples/counter/counter.py"
```

- **Model**: everything the app knows. Frozen, so nothing can change it by accident.
- **Messages**: everything that can happen. One small dataclass each, named after a fact.
- **`update`**: takes the model and a message, returns a *new* model.
  `assert_never` makes pyright complain if you forget a message.
- **`view`**: turns the model into HTML. `on_click(ClickedIncrement())` says which
  message a click sends.

## Start it in the browser

`main.py` starts the app inside the element with `id="app"`. It is a separate file
because it only works in the browser, while `counter.py` also runs in pytest.

```python title="main.py"
--8<-- "examples/counter/main.py"
```

`index.html` loads Pyodide, copies the Python files into it and imports `main.py`:

```html title="index.html"
--8<-- "examples/counter/index.html"
```

To make your own app, copy `examples/counter/` and change it.
