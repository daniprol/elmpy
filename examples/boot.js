// Starts an example in the browser:
// 1. load Pyodide (CPython compiled to WebAssembly),
// 2. copy elmpy and the example's Python files into Pyodide's in-memory file system,
// 3. import the example's main.py, which starts the program.

// Keep this version in sync with `pyodide-py` in pyproject.toml.
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";

const ELMPY_FILES = ["__init__.py", "_message.py", "html.py", "vdom.py", "runtime.py", "browser.py"];

export async function start(exampleFiles) {
  const pyodide = await loadPyodide();
  const elmpySource = new URL("../src/elmpy/", import.meta.url);
  await copyFiles(pyodide, elmpySource, ELMPY_FILES, "/app/elmpy");
  await copyFiles(pyodide, new URL("./", document.baseURI), exampleFiles, "/app");
  pyodide.runPython("import sys; sys.path.insert(0, '/app')");
  pyodide.pyimport("main");
}

async function copyFiles(pyodide, baseUrl, names, directory) {
  pyodide.FS.mkdirTree(directory);
  for (const name of names) {
    const response = await fetch(new URL(name, baseUrl));
    if (!response.ok) throw new Error(`Could not fetch ${name}: ${response.status}`);
    pyodide.FS.writeFile(`${directory}/${name}`, await response.text());
  }
}
