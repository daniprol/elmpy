# Examples

These are the real apps from the repository's `examples/` folder, running in your
browser on Pyodide. They may take a few seconds to start.

<!-- The `sandbox` attribute stops the todo app's `autofocus` from scrolling this page. -->

## Counter

<iframe class="elmpy-demo" src="../live/examples/counter/" title="Counter example" loading="lazy"
  sandbox="allow-scripts allow-same-origin allow-forms"></iframe>

??? example "counter.py"
    ```python
    --8<-- "examples/counter/counter.py"
    ```

## Todo list

A text input, a form, checkboxes and a list that grows and shrinks.

<iframe class="elmpy-demo" src="../live/examples/todo/" title="Todo example" loading="lazy"
  sandbox="allow-scripts allow-same-origin allow-forms"></iframe>

??? example "todo.py"
    ```python
    --8<-- "examples/todo/todo.py"
    ```

??? example "test_todo.py"
    ```python
    --8<-- "examples/todo/test_todo.py"
    ```
