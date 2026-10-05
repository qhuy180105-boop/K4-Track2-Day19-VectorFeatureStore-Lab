"""Export all 8 notebooks as executed .ipynb files with full outputs in submission/notebooks/"""
import sys
import os
from pathlib import Path
import jupytext
from nbclient import NotebookClient
import nbformat

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"
OUT_DIR = ROOT / "submission" / "notebooks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Add ROOT to sys.path so nbclient process environment can import local modules
os.environ["PYTHONPATH"] = f"{NB_DIR}{os.pathsep}{ROOT / 'app'}{os.pathsep}{ROOT / 'scripts'}{os.pathsep}{ROOT}{os.pathsep}" + os.environ.get("PYTHONPATH", "")

def export_executed_notebooks():
    notebooks = sorted(p for p in NB_DIR.glob("[0-9]*.py"))
    print(f"Exporting {len(notebooks)} executed notebooks to {OUT_DIR}...\n")

    for py_path in notebooks:
        ipynb_name = py_path.stem + ".ipynb"
        out_path = OUT_DIR / ipynb_name
        print(f"Processing {py_path.name} -> {ipynb_name}...")

        # 1. Read Jupytext .py to NotebookNode
        nb = jupytext.read(py_path)
        nb.metadata.setdefault("language_info", {})["name"] = "python"

        # 2. Execute notebook with nbclient, using notebooks/ as working directory
        client = NotebookClient(nb, timeout=600, kernel_name="python3", allow_errors=False, exec_cwd=str(NB_DIR))
        client.execute()

        # 3. Write executed notebook
        nbformat.write(nb, out_path)
        print(f"  ✓ Saved executed notebook: {out_path.name} ({out_path.stat().st_size / 1024:.1f} KB)")

    print("\nAll 8 notebooks exported with full outputs successfully!")

if __name__ == "__main__":
    export_executed_notebooks()
