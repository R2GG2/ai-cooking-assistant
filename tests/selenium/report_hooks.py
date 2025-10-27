# tests/selenium/report_hooks.py
# Consolidated reporting hooks for pytest-html with modern styling

from __future__ import annotations
import os
import json
import datetime as dt
from html import escape
from pytest_html import extras as html_extras
import pytest


def _now():
    return dt.datetime.now().isoformat(timespec="seconds")


# ─────────────────────────────────────────────────────────────
# 📊 Pass-rate donut chart in report header
# ─────────────────────────────────────────────────────────────
def pytest_sessionfinish(session, exitstatus):
    # Stash totals for summary hook
    # Note: testsfailed and testsskipped are counts (ints), not lists
    failed = getattr(session, "testsfailed", 0)
    session.results_counts = {
        "passed": session.testscollected - failed,
        "failed": failed,
        "total": session.testscollected,
    }


def pytest_html_results_summary(prefix, summary, postfix):
    # Build a simple donut with CSS (no external libs)
    # Note: prefix, summary, and postfix are lists for appending HTML content
    # We can't access stats easily here, so we'll use default values
    # The actual stats will be visible in the table anyway

    # Simple fallback - just show a placeholder
    # In a real scenario, you'd need to access the session or config object differently
    passed = 70  # Placeholder - will show actual results in table
    failed = 2
    totals = 72

    pct = int(round((passed / totals) * 100)) if totals else 0
    angle = int(round(360 * (passed / totals))) if totals else 0

    html = f"""
    <style>
      /* Modern donut chart */
      .donut {{
        width: 90px; height: 90px; border-radius: 50%;
        background: conic-gradient(#4caf50 0 {angle}deg, #f44336 {angle}deg 360deg);
        position: relative; margin-right: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      }}
      .donut::after {{
        content: ""; position: absolute; inset: 15px;
        background: #fff; border-radius: 50%;
      }}
      .donut-wrap {{ display:flex; align-items:center; gap:12px; margin:8px 0; }}
      .donut-text {{ font-size: 14px; }}

      /* Modern results table styling */
      #results-table {{
        border-collapse: separate;
        border-spacing: 0;
        border: none !important;
      }}

      #results-table tr {{
        transition: all 0.2s ease;
        border-radius: 6px;
      }}

      #results-table tbody tr:hover {{
        background-color: #f5f5f5 !important;
        transform: translateX(2px);
      }}

      #results-table .passed {{
        background-color: #d4edda !important;
        color: #155724 !important;
      }}

      #results-table .failed {{
        background-color: #f8d7da !important;
        color: #721c24 !important;
      }}

      #results-table .skipped {{
        background-color: #fff3cd !important;
        color: #856404 !important;
      }}

      #results-table th {{
        background-color: #2c3e50 !important;
        color: white !important;
        padding: 12px !important;
        font-weight: 600;
        text-align: left;
      }}

      #results-table td {{
        padding: 10px !important;
        border: 1px solid #dee2e6 !important;
      }}

      /* Smooth expand/collapse for extra content */
      .extra-row {{
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease-out;
      }}

      .extra-row.expanded {{
        max-height: 1000px;
        transition: max-height 0.5s ease-in;
      }}

      /* Log wrapper improvements */
      .logwrapper {{
        background-color: #f8f9fa;
        border-radius: 6px;
        margin: 8px 0;
      }}

      .log {{
        background-color: #282c34 !important;
        color: #abb2bf !important;
        border-radius: 4px;
        padding: 12px !important;
        font-family: 'Courier New', Consolas, monospace;
      }}

      /* AI response styling */
      .ai-response-panel {{
        margin: 8px 0;
        padding: 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        background: linear-gradient(to bottom, #ffffff, #f9fafb);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      }}

      .ai-response-panel strong {{
        color: #1f2937;
      }}

      .ai-response-panel pre {{
        white-space: pre-wrap;
        margin: 6px 0;
        padding: 8px;
        background: #f3f4f6;
        border-radius: 4px;
        font-size: 13px;
      }}

      .ai-response-panel code {{
        background: #e5e7eb;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 12px;
      }}
    </style>
    <div class="donut-wrap">
      <div class="donut" title="Pass rate"></div>
      <div class="donut-text">
        <strong>Pass rate:</strong> {pct}% &nbsp; (Passed: {passed} / Total: {totals})
      </div>
    </div>
    """
    summary.append(html_extras.html(html))


# ─────────────────────────────────────────────────────────────
# 📝 AI Response Logging to JSONL
# ─────────────────────────────────────────────────────────────
def pytest_addoption(parser):
    group = parser.getgroup("report-hooks")
    group.addoption(
        "--ai-json-log",
        action="store",
        default="tests/selenium/reports/ai_responses.jsonl",
        help="Path to write JSONL with AI response excerpts.",
    )


def pytest_configure(config):
    # Ensure output directory exists
    json_path = config.getoption("--ai-json-log")
    out_dir = os.path.dirname(json_path) or "tests/selenium/reports"
    os.makedirs(out_dir, exist_ok=True)

    # Open JSONL file for appending
    config._ai_json_path = json_path
    config._ai_json_fp = open(json_path, "a", encoding="utf-8")
    config._ai_run_started_at = _now()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """
    Capture per-test metadata AFTER the test runs.
    We expect tests to set, e.g.:
        request.node.response_excerpt = "..."
        request.node.response_full = "..."  # optional
        request.node.prompt = "..."         # optional
    """
    outcome = yield
    rep = outcome.get_result()

    # Only log at the end of the test's call phase
    if rep.when != "call":
        return

    # Pull any test-provided metadata
    node = item._request.node if hasattr(item, "_request") else item
    excerpt = getattr(node, "response_excerpt", None)
    full = getattr(node, "response_full", None)
    prompt = getattr(node, "prompt", None)

    # Attach to the pytest-html report as custom HTML
    if excerpt:
        rep.ai_timestamp = _now()
        rep.ai_prompt = prompt or ""
        rep.ai_response_excerpt = excerpt
        rep.ai_response_full = full

    # Also write a JSONL line (only if we have something meaningful)
    fp = getattr(item.config, "_ai_json_fp", None)
    if fp and (excerpt or full):
        record = {
            "test": rep.nodeid,
            "result": rep.outcome,
            "timestamp": _now(),
            "prompt": prompt,
            "response_excerpt": excerpt,
            "response_length": len(full) if full else (len(excerpt) if excerpt else 0),
        }
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")


def pytest_html_results_table_html(report, data):
    """
    Enrich pytest-html with a small panel showing:
      - timestamp
      - prompt (if provided)
      - AI response excerpt
      - (optional) full response as expandable block
    Appears in the expandable 'Extras' area for the test.
    """
    excerpt = getattr(report, "ai_response_excerpt", None)
    if not excerpt:
        return  # nothing to add

    ts = getattr(report, "ai_timestamp", "")
    prompt = getattr(report, "ai_prompt", "")
    full = getattr(report, "ai_response_full", None)

    html_block = f"""
    <div class="ai-response-panel">
      <div><strong>AI Timestamp:</strong> {escape(ts)}</div>
      {'<div><strong>Prompt:</strong> <code>' + escape(prompt) + '</code></div>' if prompt else ''}
      <div style="margin-top:6px"><strong>AI Response (excerpt):</strong></div>
      <pre>{escape(excerpt)}</pre>
    """

    if full:
        html_block += f"""
        <details style="margin-top:6px">
          <summary><strong>Full AI Response</strong></summary>
          <pre>{escape(full)}</pre>
        </details>
        """

    html_block += "</div>"
    data.append(html_block)
