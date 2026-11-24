# Runs in the browser only. todo.py stays importable in pytest.
import todo
from elmpy import browser

browser.sandbox(init=todo.Model(), update=todo.update, view=todo.view)
