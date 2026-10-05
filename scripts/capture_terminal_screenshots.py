"""Capture terminal execution log screenshots for verify_lite and pytest"""

import subprocess
import sys
from pathlib import Path
from html2image import Html2Image

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "submission" / "screenshots"
SCRATCH_DIR = ROOT / "scratch" / "html_exports"

def run_and_capture_terminal(cmd: list[str], title: str, filename: str):
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output_text = res.stdout + "\n" + res.stderr

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
    font-size: 14px;
    padding: 20px;
    margin: 0;
}}
.terminal-card {{
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}}
.header {{
    color: #58a6ff;
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 12px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
}}
pre {{
    color: #e6edf3;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 0;
}}
.pass {{ color: #56d364; font-weight: bold; }}
</style>
</head>
<body>
<div class="terminal-card">
  <div class="header">Terminal Execution — {title}</div>
  <pre>{output_text}</pre>
</div>
</body>
</html>
"""
    html_file = SCRATCH_DIR / f"{filename}.html"
    html_file.write_text(html, encoding="utf-8")

    hti = Html2Image(output_path=str(SCREENSHOT_DIR))
    hti.screenshot(html_file=str(html_file), save_as=f"{filename}.png", size=(1200, 800))
    print(f"Captured terminal screenshot -> {filename}.png")

def main():
    run_and_capture_terminal([sys.executable, "scripts/verify_lite.py"], "verify_lite.py", "verify_lite_terminal")
    run_and_capture_terminal([sys.executable, "-m", "pytest", "-v"], "pytest test suite", "pytest_terminal")

if __name__ == "__main__":
    main()
