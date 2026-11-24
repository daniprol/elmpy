# AGENTS.md

Guidance for AI coding agents (and humans) working on elmpy.

## What this is

elmpy brings the Elm Architecture (model, update, view) to Python in the browser,
on Pyodide. The API follows [Foldkit](https://github.com/foldkit/foldkit):
`div([attributes], [children])`, `Message`, `map_html`.

**It is a learning project.** The code is meant to be read and understood in one
sitting. When choosing between clever and obvious, choose obvious. When choosing
between a feature and less code, ask first.

## Layout

```
src/elmpy/
  html.py       view data (Element, Text, attributes, event handlers) and builders
  vdom.py       Renderer: create / patch / destroy DOM nodes
  runtime.py    Program: the message → update → view → patch loop
  browser.py    the ONLY module that imports `js` or `pyodide`
  testing.py    fake DOM + sandbox() for pytest
  _message.py   the shared covariant `Message` TypeVar (private)
examples/
  boot.js       loads Pyodide, copies Python files into it, imports main.py
  counter/      smallest app: counter.py (the app), main.py (browser entry), test
  todo/         input, form submit, checkboxes, a list
tests/          library tests, plus type_checks.py for pyright
e2e/            Playwright tests: the examples in real Chromium on Pyodide
typings/js.pyi  minimal stub for Pyodide's `js` module
```

## Commands

```sh
uv sync                        # install Python 3.14 and dev tools
uv run prek run --all-files    # everything CI runs: hygiene, uv lock, ruff, pyright, pytest
uv run pytest                  # tests only
uv run pyright                 # type check only (strict)
uv run playwright install chromium && uv run pytest e2e   # browser tests (slower)
uv run python -m http.server   # then open http://localhost:8000/examples/todo/
```

Run `uv run prek run --all-files` before every commit. CI runs exactly that,
plus the browser tests in `e2e/`.

## Rules

- **Simple first.** No new dependencies, code generation, metaclasses or plugin
  systems. Add a tag, attribute or event only when an example needs it.
- **Readable names.** Full words (`Message`, `attributes`, `to_message`), no
  abbreviations. Short docstrings that say *why*, in plain English.
- **Immutable data.** Models, messages and view nodes are `@dataclass(frozen=True)`.
  Use tuples, not lists, inside them. Update with `dataclasses.replace`.
- **Fact-named messages**, Foldkit style: `ClickedIncrement`, `ChangedDraft`,
  `GotCounter(message)`. Each module defines `type Message = A | B | ...` and
  `update` ends with `case _: assert_never(message)`.
- **The browser stays at the edge.** Only `browser.py` (and `examples/*/main.py`)
  may import `js` or `pyodide`. Everything else must run in plain CPython pytest.
- **No raw HTML.** Text goes through `createTextNode`, attributes through
  `setAttribute`. Never use `innerHTML`.
- **Pyodide version** is pinned in two places that must match: the URL in
  `examples/boot.js` and `pyodide-py` in `pyproject.toml`.

## Typing

pyright in strict mode is the one checker that gates CI. Keep it at 0 errors and
0 warnings, without `Any` leaking into public signatures.

- Generic *classes* (`Element`, `EventHandler`) use the covariant `Message` TypeVar
  from `_message.py`. pyright would infer them invariant on Python 3.13+, which
  rejects ordinary views. Functions and type aliases use PEP 695 syntax (`def f[Message]`).
- Tag functions declare `[Message = Never]`, so an element without handlers is
  `Element[Never]` and fits in any view.
- Take `Sequence[...]` parameters, not `list[...]`.
- `tests/type_checks.py` holds mistakes pyright must catch, each marked
  `# pyright: ignore[rule]`. If one stops being an error, pyright fails. Add a case
  there when you change the typing of the public API.

## Tests

- Test `update` as a pure function, and views through `elmpy.testing.sandbox`.
- Test the diff with the fake DOM. `FakeDocument.log` records every DOM change,
  so assert that a patch did *only* what it should (see `tests/test_vdom.py`).
- New DOM features need the matching method on the fake DOM. Keep the fake
  small: implement only what `vdom.py` calls.
- Example apps have their tests next to them (`examples/*/test_*.py`).
- `e2e/` checks each example once in a real browser: that it loads and the main
  interactions work. Keep the detailed checks in the fast fake-DOM tests.

## Workflow

- Never commit to `main` directly. Work on a branch and open a pull request.
- Small, focused commits and PRs. Explain *why* in the PR description.

## Roadmap (not in the code yet)

Commands and subscriptions (`Command[Message]`, `Subscription[Message]`,
`map_commands`, `map_subscriptions`), keyed lists, routing, time-travel debugging,
PyPI release. Don't build ahead of the milestone being worked on.
