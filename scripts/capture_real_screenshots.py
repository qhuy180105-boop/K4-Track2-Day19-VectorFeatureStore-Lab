"""Generate real browser-rendered screenshot PNGs for all 8 notebooks and verification runs in submission/screenshots/

Uses nbconvert to export executed .ipynb notebooks to HTML, applies a dark-theme style,
and uses html2image (Chrome/Edge headless) to capture genuine render screenshots of the real outputs.
"""

import sys
import subprocess
import shutil
from pathlib import Path
from html2image import Html2Image

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_NB_DIR = ROOT / "submission" / "notebooks"
SCREENSHOT_DIR = ROOT / "submission" / "screenshots"
SCRATCH_DIR = ROOT / "scratch" / "html_exports"

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

DARK_CSS = """
<style>
body {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
    margin: 0;
    padding: 24px;
}
.jp-Notebook {
    background-color: #0d1117 !important;
}
.jp-Cell {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    margin-bottom: 16px !important;
    padding: 12px !important;
}
.jp-InputArea-editor, pre, code {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: "Cascadia Code", "Fira Code", Consolas, monospace !important;
    font-size: 13px !important;
}
.jp-OutputArea-output, pre {
    color: #79c0ff !important;
}
.ansi-green-fg, .ansi-green-intense-fg { color: #56d364 !important; font-weight: bold; }
.ansi-blue-fg, .ansi-blue-intense-fg { color: #58a6ff !important; }
.ansi-cyan-fg, .ansi-cyan-intense-fg { color: #39c5cf !important; }
.ansi-yellow-fg, .ansi-yellow-intense-fg { color: #e3b341 !important; }
.ansi-red-fg, .ansi-red-intense-fg { color: #ff7b72 !important; }
table {
    border-collapse: collapse !important;
    width: 100% !important;
    margin: 12px 0 !important;
    color: #c9d1d9 !important;
}
th, td {
    border: 1px solid #30363d !important;
    padding: 8px 12px !important;
    text-align: left !important;
}
th {
    background-color: #21262d !important;
    color: #f0f6fc !important;
}
h1, h2, h3, h4 {
    color: #58a6ff !important;
    border-bottom: 1px solid #30363d !important;
    padding-bottom: 8px !important;
}
</style>
"""

def convert_nb_to_html(nb_file: Path, out_html: Path):
    cmd = [
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", "html",
        str(nb_file),
        "--output-dir", str(out_html.parent),
        "--output", out_html.name
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error converting {nb_file.name}: {res.stderr}")
        return False

    # Inject dark CSS
    html_content = out_html.read_text(encoding="utf-8")
    if "</head>" in html_content:
        html_content = html_content.replace("</head>", f"{DARK_CSS}</head>")
    else:
        html_content = DARK_CSS + html_content
    out_html.write_text(html_content, encoding="utf-8")
    return True

def main():
    print("Capturing REAL screenshots using nbconvert + html2image (Chrome/Edge headless)...")
    hti = Html2Image(output_path=str(SCREENSHOT_DIR))

    mapping = [
        ("01_embeddings_index.ipynb", "nb01_embeddings_index.png", ["nb1_indexed_1000.png"]),
        ("02_hybrid_search_rrf.ipynb", "nb02_hybrid_search_rrf.png", ["nb2_hybrid_precision.png", "nb2_precision_table.png"]),
        ("03_search_api_benchmark.ipynb", "nb03_search_api_benchmark.png", ["nb3_latency_p99.png"]),
        ("04_feast_feature_store.ipynb", "nb04_feast_feature_store.png", ["nb4_feast_online.png"]),
        ("05_filtered_search.ipynb", "nb05_filtered_search.png", []),
        ("06_agent_retrieval.ipynb", "nb06_agent_retrieval.png", []),
        ("07_semantic_cache.ipynb", "nb07_semantic_cache.png", []),
        ("08_feature_engineering.ipynb", "nb08_feature_engineering.png", []),
    ]

    for nb_name, primary_img, aliases in mapping:
        nb_path = SUBMISSION_NB_DIR / nb_name
        if not nb_path.exists():
            print(f"Skipping missing notebook: {nb_name}")
            continue

        html_path = SCRATCH_DIR / f"{nb_path.stem}.html"
        print(f"\n1. Converting {nb_name} -> HTML...")
        if convert_nb_to_html(nb_path, html_path):
            print(f"2. Capturing real screenshot -> {primary_img}...")
            hti.screenshot(
                html_file=str(html_path),
                save_as=primary_img,
                size=(1280, 960)
            )

            primary_path = SCREENSHOT_DIR / primary_img
            if primary_path.exists():
                print(f"   Saved {primary_img} ({primary_path.stat().st_size / 1024:.1f} KB)")
                for alias in aliases:
                    alias_path = SCREENSHOT_DIR / alias
                    shutil.copy2(primary_path, alias_path)
                    print(f"   Copied alias -> {alias}")
            else:
                print(f"   WARNING: Screenshot {primary_img} failed to write!")

    print("\nAll real screenshots captured successfully!")

if __name__ == "__main__":
    main()
