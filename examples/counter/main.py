# Runs in the browser only. counter.py stays importable in pytest.
import counter
from elmpy import browser

browser.sandbox(init=counter.Model(), update=counter.update, view=counter.view)
