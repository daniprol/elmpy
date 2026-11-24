# How it works

## The loop

```mermaid
flowchart LR
    click["User clicks"] -->|message| update
    update -->|new model| view
    view -->|new Html| patch["Patch the DOM"]
    patch --> click
```

1. An event handler turns a DOM event into a **message**, such as `ClickedIncrement()`.
2. `update(model, message)` returns a **new model**. It never changes the old one.
3. `view(model)` returns the whole page as plain data (`Html`).
4. elmpy compares the new `Html` with the previous one and changes only the DOM
   nodes that differ.

Messages that arrive while elmpy is still updating wait in a queue, so `update`
always sees one message at a time.

## The pieces

| Module | Job |
|---|---|
| `elmpy.html` | Builds `Html`: tags, attributes, event handlers, `map_html` |
| `elmpy.vdom` | The diff. Creates DOM nodes, patches them, removes them |
| `elmpy.runtime` | `Program`: holds the model and runs the loop |
| `elmpy.browser` | Starts a `Program` on a real page. The only module that uses Pyodide |
| `elmpy.testing` | A small fake DOM, so the same `Program` runs in pytest |

## The diff, in short

- **Same tag:** keep the DOM node, update its attributes, then patch the children.
- **Different tag, or text vs element:** build a new node and swap it in.
- **Children** are matched by position: first with first, second with second.
  Extra new ones are appended, missing ones removed.
- **`value` and `checked`** are set as DOM properties, and only when they differ
  from what is on the page. That keeps the cursor in place while you type.
- **Event listeners:** each element has at most one listener per event name. The
  listener looks up the current handler when the event fires, so a re-render never
  adds or removes listeners.
