---
hide:
  - navigation
  - toc
---

<div class="elmpy-hero" markdown>

# elmpy

The Elm Architecture for Python, <mark>running in your browser</mark> on Pyodide.
Describe your app as plain data and pure functions. elmpy draws it and keeps the page up to date.

[Get started](get-started.md){ .md-button .md-button--primary }
[See it running](examples.md){ .md-button }

</div>

<div class="elmpy-split" markdown>

<div markdown>

```python
--8<-- "examples/counter/counter.py"
```

</div>

<div markdown>

**This code, running right here:**

<iframe class="elmpy-demo" src="live/examples/counter/" title="The counter example, running"
  sandbox="allow-scripts allow-same-origin allow-forms"></iframe>

That is the whole app. There is no JavaScript to write, nothing is mutated,
and you can test it with pytest.

</div>

</div>

## Why

- **One way data flows.** A click becomes a message, `update` turns the old model
  into a new one, `view` turns the model into HTML. That's the whole app.
- **Plain Python.** Frozen dataclasses, `match`, and type hints. pyright tells you
  when a child view's messages aren't wrapped for its parent.
- **Small enough to read.** The library is a few hundred lines. Read
  [How it works](how-it-works.md), then read the source.

!!! note "Early days"
    elmpy is a learning project. This first version has no side effects yet
    (no HTTP, no timers). Those come next.
