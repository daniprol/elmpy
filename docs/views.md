# Views

A view returns `Html[Message]`: HTML that can only produce your `Message` type.

## Elements, attributes and text

Every tag takes a list of attributes and a list of children:

```python
div([class_("card"), id_("intro")], [
    h1([], [text("Hello")]),
    input_([placeholder("Your name"), value(model.name)]),  # no children
])
```

Names that clash with Python get a trailing underscore: `class_`, `id_`, `type_`,
`for_`, `input_`. For anything not built in, use `element("tag", ...)` and
`attribute("name", "value")`.

Attributes are ordinary values, so conditions are ordinary Python:

```python
li([class_("done")] if todo.done else [], [text(todo.title)])
```

`True` and `False` add or remove boolean attributes: `disabled(not model.draft)`.

## Events

| Handler | Sends |
|---|---|
| `on_click(message)` | `message` |
| `on_input(to_message)` | `to_message(text)` on every keystroke |
| `on_check(to_message)` | `to_message(checked)` when a checkbox changes |
| `on_submit(message)` | `message`, and stops the page from reloading |
| `on(event, to_message)` | `to_message(Event)` for any DOM event |

Handlers receive Python values, never JavaScript objects.

## Embedding a child view

Say a page shows a counter. The counter's view produces `counter.Message`, but the
page's `update` expects the page's own `Message`. Wrap the child's messages with
`map_html`:

```python
@dataclass(frozen=True)
class GotCounter:
    message: counter.Message


type Message = GotCounter | ClickedReset


def view(model: Model) -> Html[Message]:
    return div([], [
        map_html(GotCounter, counter.view(model.counter)),
        button([on_click(ClickedReset())], [text("Reset")]),
    ])
```

Forget the `map_html`, and pyright reports an error before you open the browser.
