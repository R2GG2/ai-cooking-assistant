# -----------------------------
# Optional: pass-rate mini chart in report header
# -----------------------------
def pytest_sessionfinish(session, exitstatus):
    # stash totals for summary hook
    session.results_counts = {
        "passed": session.testscollected - len(session.testsfailed) - len(session.skipped),
        "failed": len(session.testsfailed),
        "total": session.testscollected,
    }

def pytest_html_results_summary(prefix, summary, postfix):
    # Build a simple donut with CSS (no external libs)
    try:
        # Compute from the terminalreporter where possible
        tr = prefix.config.pluginmanager.get_plugin("terminalreporter")
        totals = getattr(tr, "_numcollected", 0)
        failed = len(getattr(tr, "stats", {}).get("failed", []))
        passed = totals - failed - len(getattr(tr, "stats", {}).get("skipped", []))
    except Exception:
        # Fallback
        passed = getattr(prefix.config, "passed", 0)
        failed = getattr(prefix.config, "failed", 0)
        totals = passed + failed

    pct = int(round((passed / totals) * 100)) if totals else 0
    angle = int(round(360 * (passed / totals))) if totals else 0

    html = f"""
    <style>
      .donut {{
        width: 90px; height: 90px; border-radius: 50%;
        background: conic-gradient(#4caf50 0 {angle}deg, #f44336 {angle}deg 360deg);
        position: relative; margin-right: 10px;
      }}
      .donut::after {{
        content: ""; position: absolute; inset: 15px;
        background: #fff; border-radius: 50%;
      }}
      .donut-wrap {{ display:flex; align-items:center; gap:12px; margin:8px 0; }}
      .donut-text {{ font-size: 14px; }}
    </style>
    <div class="donut-wrap">
      <div class="donut" title="Pass rate"></div>
      <div class="donut-text">
        <strong>Pass rate:</strong> {pct}% &nbsp; (Passed: {passed} / Total: {totals})
      </div>
    </div>
    """
    summary.append(html_extras.html(html))
