"""A todo list: text input, form submit, checkboxes and a list that grows and shrinks."""

from dataclasses import dataclass, replace
from typing import assert_never

from elmpy.html import (
    Html,
    autofocus,
    button,
    checked,
    class_,
    disabled,
    form,
    h1,
    input_,
    label,
    li,
    main,
    on_check,
    on_click,
    on_input,
    on_submit,
    p,
    placeholder,
    text,
    type_,
    ul,
    value,
)

# --- Model -----------------------------------------------------------------


@dataclass(frozen=True)
class Todo:
    id: int
    title: str
    done: bool = False


@dataclass(frozen=True)
class Model:
    draft: str = ""
    todos: tuple[Todo, ...] = ()  # a tuple, not a list, so the model stays immutable
    next_id: int = 1


# --- Messages --------------------------------------------------------------


@dataclass(frozen=True)
class ChangedDraft:
    text: str


@dataclass(frozen=True)
class SubmittedDraft: ...


@dataclass(frozen=True)
class ToggledTodo:
    id: int
    done: bool


@dataclass(frozen=True)
class ClickedDelete:
    id: int


type Message = ChangedDraft | SubmittedDraft | ToggledTodo | ClickedDelete


# --- Update ----------------------------------------------------------------


def update(model: Model, message: Message) -> Model:
    match message:
        case ChangedDraft(draft):
            return replace(model, draft=draft)
        case SubmittedDraft():
            title = model.draft.strip()
            if not title:
                return model
            todo = Todo(id=model.next_id, title=title)
            return Model(draft="", todos=(*model.todos, todo), next_id=model.next_id + 1)
        case ToggledTodo(todo_id, done):
            todos = tuple(
                replace(todo, done=done) if todo.id == todo_id else todo for todo in model.todos
            )
            return replace(model, todos=todos)
        case ClickedDelete(todo_id):
            return replace(model, todos=tuple(todo for todo in model.todos if todo.id != todo_id))
        case _:
            assert_never(message)


# --- View ------------------------------------------------------------------


def view(model: Model) -> Html[Message]:
    left = sum(not todo.done for todo in model.todos)
    return main(
        [class_("todo-app")],
        [
            h1([], [text("Todos")]),
            form(
                [on_submit(SubmittedDraft())],
                [
                    input_(
                        [
                            placeholder("What needs doing?"),
                            value(model.draft),
                            on_input(ChangedDraft),
                            autofocus(True),
                        ]
                    ),
                    button([disabled(not model.draft.strip())], [text("Add")]),
                ],
            ),
            ul([], [view_todo(todo) for todo in model.todos]),
            p([class_("left")], [text(f"{left} left")]),
        ],
    )


def view_todo(todo: Todo) -> Html[Message]:
    return li(
        [class_("done")] if todo.done else [],
        [
            label(
                [],
                [
                    input_(
                        [
                            type_("checkbox"),
                            checked(todo.done),
                            on_check(lambda done: ToggledTodo(todo.id, done)),
                        ]
                    ),
                    text(todo.title),
                ],
            ),
            button([class_("delete"), on_click(ClickedDelete(todo.id))], [text("Delete")]),
        ],
    )
