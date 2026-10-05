"""Execute each notebook one by one with print statements to track progress."""
import os
import sys
from pathlib import Path
import jupytext
from nbclient import NotebookClient
import nbformat

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"
OUT_DIR = ROOT / "submission" / "notebooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

os.environ["PYTHONPATH"] = f"{NB_DIR}{os.pathsep}{ROOT / 'app'}{os.pathsep}{ROOT / 'scripts'}{os.pathsep}{ROOT}{os.pathsep}" + os.environ.get("PYTHONPATH", "")

def main():
    notebooks = sorted(p for p in NB_DIR.glob("[0-9]*.py"))
    for py_path in notebooks:
        ipynb_name = py_path.stem + ".ipynb"
        out_path = OUT_DIR / ipynb_name
        print(f"Executing {py_path.name} ...", flush=True)

        nb = jupytext.read(py_path)
        nb.metadata.setdefault("language_info", {})["name"] = "python"

        client = NotebookClient(nb, timeout=120, kernel_name="python3", allow_errors=True, exec_cwd=str(NB_DIR))
        client.execute()

        nbformat.write(nb, out_path)
        print(f"  ✓ Saved: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)\n", flush=True)

if __name__ == "__main__":
    main()
