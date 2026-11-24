import todo
from elmpy.testing import sandbox


def test_submit_adds_a_todo_and_clears_the_draft() -> None:
    model = todo.update(todo.Model(draft="  Buy milk "), todo.SubmittedDraft())
    assert model == todo.Model(draft="", todos=(todo.Todo(1, "Buy milk"),), next_id=2)


def test_blank_draft_is_ignored() -> None:
    model = todo.Model(draft="   ")
    assert todo.update(model, todo.SubmittedDraft()) == model


def test_add_toggle_and_delete_on_the_page() -> None:
    program, page = sandbox(todo.Model(), todo.update, todo.view)

    for title in ["Buy milk", "Walk dog"]:
        page.find("input").type(title)
        page.find("form").submit()
    assert [item.text for item in page.find_all("li")] == ["Buy milkDelete", "Walk dogDelete"]
    assert page.find("input").value == ""

    first = page.find_all("li")[0]
    first.find("input").toggle()
    assert first.attributes == {"class": "done"}
    assert page.find("p").text == "1 left"

    first.find("button", text="Delete").click()
    assert [item.text for item in page.find_all("li")] == ["Walk dogDelete"]
    assert program.model.todos == (todo.Todo(2, "Walk dog"),)
