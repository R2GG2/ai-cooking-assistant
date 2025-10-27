import json
from datetime import datetime
from pathlib import Path   # ← this one must be present


def generate_html_test_report(json_path, output_html_path, title="AI Cooking Assistant – Test Report"):
    """
    Reads a test_results.json file and generates a clean HTML report.
    Works for both unit and Selenium test result formats.
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

    # Handle both {"tests": [...]} and plain list formats
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

    # Determine banner
    if failed == 0 and total > 0:
        summary_banner = "✅ All tests passed successfully!"
        banner_color = "green"
    elif failed > 0:
        summary_banner = f"⚠️ {failed} test(s) failed."
        banner_color = "red"
    else:
        summary_banner = "No tests found."
        banner_color = "gray"

    # Build HTML head
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
    <h1>{title}</h1>
    <h2 style='color:{banner_color}'>{summary_banner}</h2>
    <div class="summary">
        <strong>Generated:</strong> {timestamp}<br>
        <strong>Total Tests:</strong> {total} |
        <span class="passed">Passed:</span> {passed} |
        <span class="failed">Failed:</span> {failed}
    </div>
    <table>
        <tr><th>Test Name</th><th>Status</th><th>Duration (s)</th></tr>
"""

    # ✅ Collapsible rows logic goes here
    for test in tests:
        name = test.get("name", "Unnamed Test")
        status = test.get("status", "unknown")
        duration = test.get("duration", "-")
        message = test.get("message", "")
        error = test.get("error", "")
        trace = test.get("trace", "")
        css_class = "passed" if status == "passed" else "failed"

        # Build optional detail section
        details = ""
        if any([message, error, trace]):
            details = f"""
        <tr class="details"><td colspan="3">
            <div class="detail-box">
                {f"<p><b>Message:</b> {message}</p>" if message else ""}
                {f"<p><b>Error:</b> {error}</p>" if error else ""}
                {f"<pre>{trace}</pre>" if trace else ""}
            </div>
        </td></tr>
        """

        html += f"""
        <tr class="summary-row" onclick="toggleDetails(this)">
            <td>{name}</td>
            <td class='{css_class}'>{status}</td>
            <td>{duration}</td>
        </tr>
        {details}
        """

    # ✅ Add footer + toggle script before </body>
    html += """
    </table>
    <footer>
        <p>Report generated automatically by the AI Cooking Assistant QA Suite.</p>
    </footer>

    <script>
    function toggleDetails(row){
        let next = row.nextElementSibling;
        if(next && next.classList.contains('details')){
            next.style.display = next.style.display === 'none' ? 'table-row' : 'none';
        }
    }
    </script>
</body>
</html>
"""

    # Write output file
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    output_html_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML report generated at {output_html_path.resolve()}")
