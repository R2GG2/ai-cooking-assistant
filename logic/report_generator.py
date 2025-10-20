# logic/report_generator.py

import json
from datetime import datetime
from pathlib import Path


def generate_html_test_report(json_path, output_html_path, title="AI Cooking Assistant – Test Report"):
    """
    Reads a test_results.json file and generates a clean HTML report.
    Works for both unit and Selenium test result formats.

    Args:
        json_path (str or Path): Path to the input JSON file with test results.
        output_html_path (str or Path): Path where the HTML file will be saved.
        title (str): Optional title for the HTML report.
    """

    json_path = Path(json_path)
    output_html_path = Path(output_html_path)

    if not json_path.exists():
        raise FileNotFoundError(f"❌ JSON file not found: {json_path}")

    # Load and parse JSON safely
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON format in {json_path}: {e}")

    # ✅ Handle both {"tests": [...]} and plain list structures
    if isinstance(data, list):
        tests = data
    elif isinstance(data, dict):
        tests = data.get("tests", [])
    else:
        raise ValueError(f"Unexpected JSON structure: {type(data)}")

    # Count results
    total = len(tests)
    passed = sum(1 for t in tests if t.get("status") == "passed")
    failed = sum(1 for t in tests if t.get("status") == "failed")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine banner text and color
    if failed == 0 and total > 0:
        summary_banner = "✅ All tests passed successfully!"
        banner_color = "green"
    elif failed > 0:
        summary_banner = f"⚠️ {failed} test(s) failed."
        banner_color = "red"
    else:
        summary_banner = "No tests found."
        banner_color = "gray"

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2em; background-color: #fafafa; }}
        h1 {{ color: #333; }}
        h2.banner {{ color: {banner_color}; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background: #eee; }}
        .passed {{ color: green; font-weight: bold; }}
        .failed {{ color: red; font-weight: bold; }}
        .summary {{ margin-bottom: 1em; font-size: 1.1em; }}
        footer {{ margin-top: 2em; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <h2 class="banner">{summary_banner}</h2>
    <div class="summary">
        <strong>Generated:</strong> {timestamp}<br>
        <strong>Total Tests:</strong> {total} |
        <span class="passed">Passed:</span> {passed} |
        <span class="failed">Failed:</span> {failed}
    </div>
    <table>
        <tr><th>Test Name</th><th>Status</th><th>Duration (s)</th></tr>
"""

    for test in tests:
        name = test.get("name", "Unnamed Test")
        status = test.get("status", "unknown")
        duration = test.get("duration", "-")
        css_class = "passed" if status == "passed" else "failed"
        html += f"<tr><td>{name}</td><td class='{css_class}'>{status}</td><td>{duration}</td></tr>"

    html += f"""
    </table>
    <footer>
        <p>Report generated automatically by the AI Cooking Assistant QA Suite.</p>
    </footer>
</body>
</html>
"""

    # Write output
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    output_html_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML report generated at {output_html_path.resolve()}")
