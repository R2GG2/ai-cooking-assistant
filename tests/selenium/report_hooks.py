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


# Global storage for category statistics (shared between hooks)
_CATEGORY_STATS = {}


# ─────────────────────────────────────────────────────────────
# 📊 Category-based statistics tracking
# ─────────────────────────────────────────────────────────────
def pytest_configure(config):
    """Initialize category tracking storage."""
    global _CATEGORY_STATS
    _CATEGORY_STATS = {}  # Reset for each test run

    # Ensure output directory exists
    json_path = config.getoption("--ai-json-log", default="tests/selenium/reports/ai_responses.jsonl")
    out_dir = os.path.dirname(json_path) or "tests/selenium/reports"
    os.makedirs(out_dir, exist_ok=True)

    # Open JSONL file for appending
    config._ai_json_path = json_path
    config._ai_json_fp = open(json_path, "a", encoding="utf-8")
    config._ai_run_started_at = _now()


def _get_test_category(nodeid: str) -> str:
    """Extract category from test node ID."""
    if "test_allergy_scenarios" in nodeid or "TestRestrictionScenarios" in nodeid:
        return "Allergy/Restrictions"
    elif "test_equipment_scenarios" in nodeid or "TestEquipmentScenarios" in nodeid:
        return "Equipment"
    elif "test_ingredients_scenarios" in nodeid or "TestIngredientScenarios" in nodeid:
        return "Ingredients"
    elif "test_meal_suggestion_logic" in nodeid:
        return "Meal Suggestions"
    elif "test_response_logic" in nodeid:
        return "Response Logic"
    elif "test_bias_logic" in nodeid or "TestBiasHandling" in nodeid:
        return "Bias Handling"
    elif "inventory_test" in nodeid:
        return "Inventory"
    elif "selenium" in nodeid or "playwright" in nodeid:
        return "UI Tests"
    else:
        return "Other"


def _humanize_test_name(nodeid: str) -> str:
    """Convert pytest node ID to human-readable test name."""
    # Extract the parametrized part (in square brackets) first
    param_part = ""
    if "[" in nodeid and "]" in nodeid:
        param_part = nodeid[nodeid.find("[")+1:nodeid.find("]")]

        # Fix common unicode escapes
        param_part = param_part.replace("\\u2019", "'")  # Right single quotation mark
        param_part = param_part.replace("\\u2018", "'")  # Left single quotation mark
        param_part = param_part.replace("\\u201c", '"')  # Left double quotation mark
        param_part = param_part.replace("\\u201d", '"')  # Right double quotation mark
        param_part = param_part.replace("\\u2013", "–")  # En dash
        param_part = param_part.replace("\\u2014", "—")  # Em dash

        # If the parameter is already a human-readable string, use it directly
        if len(param_part) > 20:  # Likely a descriptive string
            return param_part
        nodeid = nodeid[:nodeid.find("[")]  # Remove parameter from nodeid

    # Extract just the test function name
    parts = nodeid.split("::")
    test_name = parts[-1] if parts else nodeid

    # Remove "test_" prefix
    if test_name.startswith("test_"):
        test_name = test_name[5:]

    # Convert snake_case to Title Case with spaces
    words = test_name.replace("_", " ").split()
    readable = " ".join(word.capitalize() for word in words)

    # Add parameter if we have one and it's short
    if param_part and len(param_part) <= 20:
        readable += f" ({param_part})"

    return readable


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
    # Build a clean summary dashboard
    # Calculate actual stats from category data
    global _CATEGORY_STATS

    passed = 0
    failed = 0
    skipped = 0
    category_count = len(_CATEGORY_STATS) if _CATEGORY_STATS else 0

    if _CATEGORY_STATS:
        for stats in _CATEGORY_STATS.values():
            passed += stats["passed"]
            failed += stats["failed"]
            skipped += stats["skipped"]

    totals = passed + failed + skipped
    pct = int(round((passed / totals) * 100)) if totals else 0

    html = f"""<link rel="stylesheet" href="assets/custom_report.css" />
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        // Rename Links header
        const headers = document.querySelectorAll('#results-table th');
        headers.forEach(function(th) {{
            if (th.textContent.trim() === 'Links') {{
                th.textContent = 'Details';
            }}
        }});

        // Disable expand buttons when no log output - improved detection
        document.querySelectorAll('.extra').forEach(function(extra) {{
            const log = extra.querySelector('.log');
            if (log) {{
                const text = log.textContent.trim();
                if (text === 'No log output captured.' || text === '' || text.length === 0) {{
                    // Find and hide the expand button
                    const row = extra.closest('tr');
                    if (row) {{
                        const prevRow = row.previousElementSibling;
                        if (prevRow) {{
                            const expanders = prevRow.querySelectorAll('.logexpander');
                            expanders.forEach(exp => {{
                                exp.style.display = 'none';
                            }});
                        }}
                    }}
                    // Also try to find expander in same row
                    const expanders = extra.querySelectorAll('.logexpander');
                    expanders.forEach(exp => {{
                        exp.style.display = 'none';
                    }});
                }}
            }}
        }});

        // Category filter functionality
        const filterBadges = document.querySelectorAll('.filter-badge');
        const tableRows = document.querySelectorAll('#results-table tbody tr');

        filterBadges.forEach(function(badge) {{
            badge.addEventListener('click', function() {{
                // Remove active class from all badges
                filterBadges.forEach(b => b.classList.remove('active'));
                // Add active class to clicked badge
                this.classList.add('active');

                const category = this.getAttribute('data-category');

                // Filter table rows
                tableRows.forEach(function(row) {{
                    const categoryBadge = row.querySelector('.category-badge');
                    if (categoryBadge) {{
                        const rowCategory = categoryBadge.textContent.trim();
                        if (category === 'all' || rowCategory === category) {{
                            row.style.display = '';
                        }} else {{
                            row.style.display = 'none';
                        }}
                    }}
                }});
            }});
        }});
    }});
    </script>
    <style>
      /* ===== GLOBAL STYLES ===== */
      body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif !important;
        line-height: 1.6 !important;
        color: #1f2937 !important;
        background: linear-gradient(to bottom, #f9fafb, #ffffff) !important;
        padding: 16px !important;
      }}

      h1 {{
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        margin-bottom: 6px !important;
        letter-spacing: -0.5px !important;
      }}

      h2 {{
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 18px !important;
        margin: 16px 0 12px 0 !important;
      }}

      /* ===== DASHBOARD CARDS ===== */
      .dashboard {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin: 12px 0;
      }}

      .stat-card {{
        background: white;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
      }}

      .stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
      }}

      .stat-card.primary {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
      }}

      .stat-card.danger {{
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
      }}

      .stat-value {{
        font-size: 32px;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 4px;
      }}

      .stat-card.primary .stat-value,
      .stat-card.danger .stat-value {{
        color: white;
      }}

      .stat-label {{
        font-size: 13px;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }}

      .stat-card.primary .stat-label,
      .stat-card.danger .stat-label {{
        color: rgba(255,255,255,0.9);
      }}

      /* ===== CATEGORY FILTER BAR ===== */
      .category-filter {{
        background: white;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
      }}

      .filter-label {{
        font-size: 14px;
        font-weight: 600;
        color: #374151;
        white-space: nowrap;
      }}

      .filter-badges {{
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }}

      .filter-badge {{
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #e5e7eb;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;
      }}

      .filter-badge:hover {{
        background: #e5e7eb;
        border-color: #d1d5db;
        transform: translateY(-1px);
      }}

      .filter-badge.active {{
        background: #3b82f6;
        color: white;
        border-color: #3b82f6;
      }}

      .filter-badge.active:hover {{
        background: #2563eb;
        border-color: #2563eb;
      }}

      /* ===== RESULTS TABLE - Modern Card-Based Design ===== */
      #results-table-container {{
        background: white;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        overflow: hidden;
        margin: 12px 0;
        border: 1px solid #e5e7eb;
      }}

      #results-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: none !important;
        margin: 0 !important;
      }}

      /* Table Header - Clean & Professional */
      #results-table thead {{
        background: linear-gradient(to bottom, #1f2937, #111827);
      }}

      #results-table th {{
        background: transparent !important;
        color: #ffffff !important;
        padding: 14px 16px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-align: left !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: none !important;
      }}

      /* Table Body - Spacious & Clean */
      #results-table tbody tr {{
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border-bottom: 1px solid #f3f4f6;
      }}

      #results-table tbody tr:last-child {{
        border-bottom: none;
      }}

      #results-table tbody tr:hover {{
        background-color: #f9fafb !important;
        transform: scale(1.002);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
      }}

      #results-table td {{
        padding: 14px 16px !important;
        border: none !important;
        border-bottom: 1px solid #f3f4f6 !important;
        font-size: 14px !important;
        vertical-align: middle !important;
      }}

      /* Test Result Status - Softer Colors */
      #results-table .passed {{
        background: linear-gradient(to right, #ecfdf5, #ffffff) !important;
        border-left: 4px solid #10b981 !important;
      }}

      #results-table .passed .col-result {{
        color: #047857 !important;
        font-weight: 600 !important;
      }}

      #results-table .failed {{
        background: linear-gradient(to right, #fef2f2, #ffffff) !important;
        border-left: 4px solid #ef4444 !important;
      }}

      #results-table .failed .col-result {{
        color: #dc2626 !important;
        font-weight: 600 !important;
      }}

      #results-table .skipped {{
        background: linear-gradient(to right, #fffbeb, #ffffff) !important;
        border-left: 4px solid #f59e0b !important;
      }}

      #results-table .skipped .col-result {{
        color: #d97706 !important;
        font-weight: 600 !important;
      }}

      #results-table .error {{
        background: linear-gradient(to right, #fef2f2, #ffffff) !important;
        border-left: 4px solid #dc2626 !important;
      }}

      /* Test Name Styling */
      #results-table .col-name {{
        font-weight: 500;
        color: #374151;
      }}

      /* Duration Styling */
      #results-table .col-duration {{
        color: #6b7280;
        font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        font-size: 13px !important;
      }}

      /* Links - Modern Blue */
      #results-table a {{
        color: #3b82f6 !important;
        text-decoration: none;
        transition: color 0.2s;
      }}

      #results-table a:hover {{
        color: #2563eb !important;
        text-decoration: underline;
      }}

      /* ===== COLLAPSIBLE CONTENT - Smooth Animations ===== */
      .extra {{
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: #f9fafb;
      }}

      .extra.expanded {{
        max-height: 2000px;
        transition: max-height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
      }}

      /* ===== LOG OUTPUT - Modern Code Block ===== */
      .logwrapper {{
        background: #1f2937;
        border-radius: 8px;
        margin: 16px 0;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      }}

      .log {{
        background: #1f2937 !important;
        color: #e5e7eb !important;
        border-radius: 0;
        padding: 20px !important;
        font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Courier New', monospace !important;
        font-size: 13px !important;
        line-height: 1.6 !important;
        overflow-x: auto;
      }}

      .logexpander {{
        background: #374151 !important;
        color: #e5e7eb !important;
        border: none !important;
        padding: 6px 12px !important;
        margin: 0 !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        display: inline-block !important;
        text-decoration: none !important;
        position: relative !important;
        float: right !important;
        top: -4px !important;
      }}

      .logexpander:hover {{
        background: #4b5563 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
      }}

      .logexpander.disabled {{
        background: #6b7280 !important;
        cursor: not-allowed !important;
        opacity: 0.5 !important;
        pointer-events: none !important;
      }}

      .collapsed {{
        display: block !important;
      }}

      .extra-row {{
        position: relative !important;
        clear: both !important;
      }}

      /* ===== AI RESPONSE PANEL - Premium Card Design ===== */
      .ai-response-panel {{
        margin: 16px 0;
        padding: 20px;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
      }}

      .ai-response-panel strong {{
        color: #111827;
        font-weight: 600;
        font-size: 14px;
      }}

      .ai-response-panel pre {{
        white-space: pre-wrap;
        margin: 12px 0;
        padding: 16px;
        background: #f9fafb;
        border-radius: 6px;
        font-size: 13px;
        line-height: 1.6;
        border: 1px solid #e5e7eb;
        font-family: 'SF Mono', Monaco, 'Courier New', monospace;
      }}

      .ai-response-panel code {{
        background: #f3f4f6;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        color: #dc2626;
        border: 1px solid #e5e7eb;
      }}

      .ai-response-panel details {{
        margin-top: 12px;
      }}

      .ai-response-panel summary {{
        cursor: pointer;
        color: #3b82f6;
        font-weight: 500;
        padding: 8px 0;
        transition: color 0.2s;
      }}

      .ai-response-panel summary:hover {{
        color: #2563eb;
      }}

      /* ===== SUMMARY INFO - Card Layout ===== */
      #environment {{
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin: 12px 0;
        border: 1px solid #e5e7eb;
      }}

      #environment td {{
        padding: 12px 16px !important;
        border: none !important;
        border-bottom: 1px solid #f3f4f6 !important;
      }}

      #environment tr:last-child td {{
        border-bottom: none !important;
      }}

      #environment tr:nth-child(odd) {{
        background-color: #f9fafb !important;
      }}

      /* ===== RESPONSIVE IMPROVEMENTS ===== */
      @media (max-width: 768px) {{
        body {{
          padding: 12px !important;
        }}

        .dashboard {{
          grid-template-columns: repeat(2, 1fr);
        }}

        #results-table td {{
          padding: 12px !important;
          font-size: 13px !important;
        }}
      }}
    </style>
    <div class="dashboard">
      <div class="stat-card primary">
        <div class="stat-value">{pct}%</div>
        <div class="stat-label">Pass Rate</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{totals}</div>
        <div class="stat-label">Total Tests</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:#10b981">{passed}</div>
        <div class="stat-label">Passed</div>
      </div>"""

    # Add failed card if there are failures
    if failed > 0:
        html += f"""
      <div class="stat-card danger">
        <div class="stat-value">{failed}</div>
        <div class="stat-label">Failed</div>
      </div>"""

    # Add skipped card if there are skipped tests
    if skipped > 0:
        html += f"""
      <div class="stat-card">
        <div class="stat-value" style="color:#f59e0b">{skipped}</div>
        <div class="stat-label">Skipped</div>
      </div>"""

    # Add categories card
    html += f"""
      <div class="stat-card">
        <div class="stat-value" style="color:#3b82f6">{category_count}</div>
        <div class="stat-label">Categories</div>
      </div>
    </div>
    """

    # Add category filter bar
    if _CATEGORY_STATS:
        html += '<div class="category-filter"><div class="filter-label">Filter by Category:</div><div class="filter-badges">'
        html += '<button class="filter-badge active" data-category="all">All ({0})</button>'.format(totals)

        for category in sorted(_CATEGORY_STATS.keys()):
            stats = _CATEGORY_STATS[category]
            total = stats["passed"] + stats["failed"] + stats["skipped"] + stats["error"]
            if total > 0:
                html += f'<button class="filter-badge" data-category="{category}">{category} ({total})</button>'

        html += '</div></div>'

    # Append HTML content directly
    summary.append(html)


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

    # Track category statistics (use global variable for access in summary hook)
    global _CATEGORY_STATS
    category = _get_test_category(rep.nodeid)

    if category not in _CATEGORY_STATS:
        _CATEGORY_STATS[category] = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}

    if rep.passed:
        _CATEGORY_STATS[category]["passed"] += 1
    elif rep.failed:
        _CATEGORY_STATS[category]["failed"] += 1
    elif rep.skipped:
        _CATEGORY_STATS[category]["skipped"] += 1
    else:
        _CATEGORY_STATS[category]["error"] += 1

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


def pytest_html_results_table_row(report, cells):
    """
    Modify the test name cell to show human-readable names.
    Also add category badge to the result cell.
    """
    # Transform the test name (second cell - testId)
    if len(cells) >= 2:
        nodeid = report.nodeid
        human_name = _humanize_test_name(nodeid)
        category = _get_test_category(nodeid)

        # Update the test name cell with human-readable name and category badge
        cells[1] = f'''<td class="col-testId">
            <span class="test-name">{escape(human_name)}</span>
            <span class="category-badge">{escape(category)}</span>
        </td>'''


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
