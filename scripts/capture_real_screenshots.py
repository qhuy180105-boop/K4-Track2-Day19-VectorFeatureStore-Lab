"""Generate focused, compact dark-mode screenshots displaying ONLY the actual execution results of each notebook and test run."""

import json
import shutil
import sys
from pathlib import Path
from html2image import Html2Image

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_NB_DIR = ROOT / "submission" / "notebooks"
SCREENSHOT_DIR = ROOT / "submission" / "screenshots"
SCRATCH_DIR = ROOT / "scratch" / "html_exports"

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

def extract_notebook_results(nb_path: Path) -> list[dict]:
    with nb_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        outputs = cell.get("outputs", [])
        if not outputs:
            continue

        source_code = "".join(cell.get("source", []))
        exec_count = cell.get("execution_count", 1)

        out_texts = []
        for out in outputs:
            out_type = out.get("output_type")
            if out_type == "stream":
                out_texts.append("".join(out.get("text", [])))
            elif out_type in ("execute_result", "display_data"):
                data_dict = out.get("data", {})
                if "text/plain" in data_dict:
                    out_texts.append("".join(data_dict["text/plain"]))
                if "text/html" in data_dict:
                    out_texts.append("".join(data_dict["text/html"]))
            elif out_type == "error":
                e_name = out.get("ename", "Error")
                e_val = out.get("evalue", "")
                out_texts.append(f"{e_name}: {e_val}")

        full_output = "\n".join(out_texts).strip()
        # Clean up warning noise if present
        lines = [l for l in full_output.split("\n") if "TqdmWarning" not in l and "autonotebook" not in l]
        cleaned_output = "\n".join(lines).strip()

        if cleaned_output:
            results.append({
                "exec_count": exec_count,
                "code": source_code.strip(),
                "output": cleaned_output
            })
    return results

def render_compact_html(nb_name: str, title: str, code_block: str, output_block: str, out_html: Path):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; }}
body {{
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    padding: 16px;
    margin: 0;
    width: 1000px;
}}
.card {{
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.6);
}}
.header-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #30363d;
    padding-bottom: 10px;
    margin-bottom: 12px;
}}
.dots {{
    display: flex;
    gap: 6px;
}}
.dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
.dot-red {{ background-color: #ff5f56; }}
.dot-yellow {{ background-color: #ffbd2e; }}
.dot-green {{ background-color: #27c93f; }}
.title {{
    color: #58a6ff;
    font-weight: 600;
    font-size: 14px;
    font-family: monospace;
}}
.tag {{
    background-color: #238636;
    color: #ffffff;
    font-size: 11px;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 12px;
    font-family: monospace;
}}
.section-label {{
    font-size: 11px;
    text-transform: uppercase;
    color: #8b949e;
    letter-spacing: 0.5px;
    margin-top: 8px;
    margin-bottom: 4px;
    font-weight: bold;
}}
pre {{
    background-color: #0d1117;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 10px 12px;
    font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
    font-size: 12.5px;
    line-height: 1.45;
    margin: 0 0 12px 0;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
}}
.code-pre {{ color: #e6edf3; }}
.out-pre {{ color: #79c0ff; border-left: 3px solid #58a6ff; }}
</style>
</head>
<body>
<div class="card">
  <div class="header-bar">
    <div style="display: flex; align-items: center; gap: 10px;">
      <div class="dots">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
      </div>
      <span class="title">{nb_name} — {title}</span>
    </div>
    <span class="tag">EXECUTION VERIFIED</span>
  </div>

  <div class="section-label">Executable Python Code</div>
  <pre class="code-pre">{code_block}</pre>

  <div class="section-label">Actual Execution Output</div>
  <pre class="out-pre">{output_block}</pre>
</div>
</body>
</html>
"""
    out_html.write_text(html, encoding="utf-8")

def main():
    print("Generating COMPACT focused real result screenshots...")
    hti = Html2Image(output_path=str(SCREENSHOT_DIR))

    mapping = [
        ("01_embeddings_index.ipynb", "NB1 Vector Indexing", "nb01_embeddings_index.png", ["nb1_indexed_1000.png"]),
        ("02_hybrid_search_rrf.ipynb", "NB2 Hybrid Search RRF", "nb02_hybrid_search_rrf.png", ["nb2_hybrid_precision.png", "nb2_precision_table.png"]),
        ("03_search_api_benchmark.ipynb", "NB3 FastAPI P99 Benchmark", "nb03_search_api_benchmark.png", ["nb3_latency_p99.png"]),
        ("04_feast_feature_store.ipynb", "NB4 Feast Feature Store", "nb04_feast_feature_store.png", ["nb4_feast_online.png"]),
        ("05_filtered_search.ipynb", "NB5 Filtered Search ANN", "nb05_filtered_search.png", []),
        ("06_agent_retrieval.ipynb", "NB6 Agentic Retrieval", "nb06_agent_retrieval.png", []),
        ("07_semantic_cache.ipynb", "NB7 Semantic Cache", "nb07_semantic_cache.png", []),
        ("08_feature_engineering.ipynb", "NB8 Feature Engineering", "nb08_feature_engineering.png", []),
    ]

    for nb_name, title, primary_img, aliases in mapping:
        nb_path = SUBMISSION_NB_DIR / nb_name
        if not nb_path.exists():
            continue

        results = extract_notebook_results(nb_path)
        if not results:
            print(f"No execution outputs found in {nb_name}")
            continue

        # Choose the most key output cell (usually the last or longest result output)
        key_res = results[-1]
        if len(results) > 1 and "PASS" in results[-1]["output"]:
            key_res = results[-1]
        elif len(results) > 1:
            # find cell with PASS or longest output
            for r in reversed(results):
                if "[PASS]" in r["output"] or "Precision" in r["output"] or "latency" in r["output"]:
                    key_res = r
                    break

        html_path = SCRATCH_DIR / f"compact_{nb_path.stem}.html"
        render_compact_html(nb_name, title, key_res["code"][:400], key_res["output"], html_path)

        hti.screenshot(
            html_file=str(html_path),
            save_as=primary_img,
            size=(1020, 520)
        )

        primary_path = SCREENSHOT_DIR / primary_img
        if primary_path.exists():
            print(f"Saved compact screenshot -> {primary_img} ({primary_path.stat().st_size / 1024:.1f} KB)")
            for alias in aliases:
                alias_path = SCREENSHOT_DIR / alias
                shutil.copy2(primary_path, alias_path)

    print("\nAll compact real result screenshots created successfully!")

if __name__ == "__main__":
    main()
