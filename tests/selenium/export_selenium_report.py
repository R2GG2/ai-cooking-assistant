# File: tests/selenium/export_selenium_report.py

import os
import sys
import pathlib
import json

# ✅ Add the absolute project root to Python's path
ROOT = pathlib.Path(__file__).resolve().parents[2]  # goes up 2 levels
sys.path.insert(0, str(ROOT))

from logic.report_generator import generate_html_test_report

# 🔧 Paths
json_path = ROOT / "test_results" / "test_results.json"
output_path = ROOT / "reports" / "selenium_report.html"

def main():
    if not json_path.exists():
        print(f"[ERROR] JSON test log not found: {json_path}")
        return

    try:
        generate_html_test_report(
            json_path=str(json_path),
            output_html_path=str(output_path)
        )
        print(f"[✓] HTML report created at: {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to generate report: {e}")

if __name__ == "__main__":
    main()
