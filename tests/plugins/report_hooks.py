# tests/plugins/report_hooks.py
from __future__ import annotations

import os
import json
import datetime as dt
from html import escape
import pytest


def _now():
    return dt.datetime.now().isoformat(timespec="seconds")


def pytest_addoption(parser):
    group = parser.getgroup("report-hooks")
    group.addoption(
        "--ai-json-log",
        action="store",
        default="reports/ai_responses.jsonl",
        help="Path to write JSONL with AI response excerpts.",
    )


def pytest_configure(config):
    # Ensure output directory exists
    json_path = config.getoption("--ai-json-log")
    out_dir = os.path.dirname(json_path) or "reports"
    os.makedirs(out_dir, exist_ok=True)

    # Open JSONL file for appending
    config._ai_json_path = json_path
    config._ai_json_fp = open(json_path, "a", encoding="utf-8")
    config._ai_run_started_at = _now()


def pytest_sessionfinish(session, exitstatus):
    # Close JSONL if we opened it
    fp = getattr(session.config, "_ai_json_fp", None)
    if fp:
        fp.close()


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
    <div style="margin:8px 0;padding:8px;border:1px solid #ddd;border-radius:6px;background:#f9f9f9">
      <div><strong>AI Timestamp:</strong> {escape(ts)}</div>
      {'<div><strong>Prompt:</strong> <code>' + escape(prompt) + '</code></div>' if prompt else ''}
      <div style="margin-top:6px"><strong>AI Response (excerpt):</strong></div>
      <pre style="white-space:pre-wrap;margin:6px 0 0 0">{escape(excerpt)}</pre>
    """

    if full:
        html_block += f"""
        <details style="margin-top:6px">
          <summary><strong>Full AI Response</strong></summary>
          <pre style="white-space:pre-wrap;margin:6px 0 0 0">{escape(full)}</pre>
        </details>
        """

    html_block += "</div>"
    data.append(html_block)

