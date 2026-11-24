# elmpy

The Elm Architecture for Python in the browser, running on [Pyodide](https://pyodide.org).

You describe your app with three plain Python pieces: a **model** (the state), an
**update** function (how messages change the state) and a **view** function (what
the state looks like). elmpy draws the view, listens for clicks and typing, and
redraws only what changed.

> Status: milestone 1, a "sandbox" with no side effects (no HTTP, no timers yet).

## Quickstart

You need [uv](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/daniprol/elmpy
cd elmpy
uv sync
uv run python -m http.server
```

Open <http://localhost:8000/examples/counter/> or <http://localhost:8000/examples/todo/>.
The first load takes a few seconds while Pyodide downloads.

## What an app looks like

```python
from dataclasses import dataclass, replace
from typing import assert_never

from elmpy.html import Html, button, div, on_click, span, text


@dataclass(frozen=True)
class Model:
    count: int = 0


@dataclass(frozen=True)
class ClickedIncrement: ...


@dataclass(frozen=True)
class ClickedDecrement: ...


type Message = ClickedIncrement | ClickedDecrement


def update(model: Model, message: Message) -> Model:
    match message:
        case ClickedIncrement():
            return replace(model, count=model.count + 1)
        case ClickedDecrement():
            return replace(model, count=model.count - 1)
        case _:
            assert_never(message)


def view(model: Model) -> Html[Message]:
    return div([], [
        button([on_click(ClickedDecrement())], [text("-")]),
        span([], [text(str(model.count))]),
        button([on_click(ClickedIncrement())], [text("+")]),
    ])
```

Start it in the browser with `elmpy.browser.sandbox(init=Model(), update=update, view=view)`
(see [`examples/counter/main.py`](examples/counter/main.py)), and test it with no browser at all:

```python
from elmpy.testing import sandbox

program, page = sandbox(Model(), update, view)
page.find("button", text="+").click()
assert page.text == "-1+"
```

To make your own app, copy [`examples/counter/`](examples/counter/) and change it.

## How it works

| Module | Job |
|---|---|
| [`html.py`](src/elmpy/html.py) | Tag, attribute and event functions that build the view as plain data |
| [`vdom.py`](src/elmpy/vdom.py) | Compares the new view with the old one and patches the DOM |
| [`runtime.py`](src/elmpy/runtime.py) | The loop: message → `update` → `view` → patch |
| [`browser.py`](src/elmpy/browser.py) | Starts a program on a real page (the only module that uses Pyodide) |
| [`testing.py`](src/elmpy/testing.py) | A small fake DOM, so apps run in pytest |

## Development

```sh
uv run prek install          # run the checks on every commit
uv run prek run --all-files  # ruff, pyright (strict), pytest and file hygiene; CI runs the same
```

See [AGENTS.md](AGENTS.md) for conventions.

## Roadmap

Commands and subscriptions (HTTP, timers), keyed lists, routing, time-travel
debugging, and a release on PyPI.
