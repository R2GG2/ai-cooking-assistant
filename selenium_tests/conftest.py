# selenium_tests/conftest.py
from pathlib import Path
import os, sys, time, socket, subprocess, signal, shutil
from datetime import datetime
from urllib.parse import quote
import pytest, requests
from contextlib import ContextDecorator
from pytest_html import extras as html_extras
import html  # built-in safe escaping
import base64


# ─────────────────────────────────────────────────────────────
# 📁 Setup: report folders and time metadata
# ─────────────────────────────────────────────────────────────
REPORT_DIR = Path(__file__).parent / "reports"
SCREEN_DIR = REPORT_DIR / "screenshots"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
SCREEN_DIR.mkdir(parents=True, exist_ok=True)

RUN_TS = os.getenv("REPORT_TS") or datetime.now().strftime("%Y%m%d-%H%M%S")
HUMAN_TS = os.getenv("REPORT_TS_HUMAN") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def pytest_html_report_title(report):
    report.title = f"Selenium UI Tests – {RUN_TS}"

def pytest_configure(config):
    md = getattr(config, "_metadata", {})
    md["Run ID"] = RUN_TS
    md["Run Timestamp"] = HUMAN_TS
    config._metadata = md

# ─────────────────────────────────────────────────────────────
# 🚀 Auto-start Flask for test session (if BASE_URL not set)
# ─────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]

def _find_free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.fixture(scope="session", autouse=True)
def flask_server():
    if os.getenv("BASE_URL"):
        yield os.environ["BASE_URL"]
        return

    port = 5000
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["PORT"] = str(port)
    env["BASE_URL"] = base_url
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTEST_RUN"] = "1"

    log_path = REPORT_DIR / "flask_server.log"
    logfile = open(log_path, "w", encoding="utf-8")
    print(f"✅ Flask started at {base_url}")

    proc = subprocess.Popen(
        [sys.executable, "-m", "ai_app.app"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=logfile,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    timeout = 45
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            raise RuntimeError(f"Flask exited early. Logs: {log_path}")
        try:
            if requests.get(f"{base_url}/health", timeout=2).status_code == 200:
                break
        except:
            pass
        time.sleep(0.5)
    else:
        raise RuntimeError(f"Flask didn't respond in {timeout}s. Logs: {log_path}")

    os.environ["BASE_URL"] = base_url
    yield base_url

    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except:
        try: proc.terminate()
        except: pass
    try: proc.wait(10)
    except: proc.kill()
    logfile.close()

# ─────────────────────────────────────────────────────────────
# 🧾 Per-Step Logger Fixture
# ─────────────────────────────────────────────────────────────
class Step(ContextDecorator):
    def __init__(self, request, name, expected="", driver=None):
        self.request = request
        self.name = name
        self.expected = html.escape(expected)
        self.actual = ""
        self.driver = driver
        self.status = "pending"
        self.start = datetime.now()
        self.screenshot_path = None
        if not hasattr(request.node, "_steps"):
            request.node._steps = []
        request.node._steps.append(self)

    def __enter__(self): return self

    def __exit__(self, exc_type, exc, tb):
        self.end = datetime.now()
        self.duration = f"{(self.end - self.start).total_seconds():.2f}s"
        self.status = "failed" if exc_type else "passed"
        self.actual = html.escape(self.actual)
        if self.status == "failed" and self.driver:
            filename = f"{self.request.node.name}_{int(self.end.timestamp())}.png"
            path = SCREEN_DIR / filename
            try:
                self.driver.save_screenshot(path)
                self.screenshot_path = path
            except: pass
        return False

@pytest.fixture
def step(request):
    def _make(name, expected="", driver=None):
        return Step(request, name, expected, driver)
    return _make

# ─────────────────────────────────────────────────────────────
# 🧩 pytest-html hook to inject steps + screenshot
# ─────────────────────────────────────────────────────────────
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when != "call":
        return
    steps = getattr(item, "_steps", [])
    if not steps:
        return

    rows = []
    for i, st in enumerate(steps, start=1):
        rows.append(
            f"<tr>"
            f"<td>{i}</td>"
            f"<td>{st.name}</td>"
            f"<td>{st.expected or ''}</td>"
            f"<td>{st.actual or ''}</td>"
            f"<td>{st.status}</td>"
            f"<td>{getattr(st, 'duration','')}</td>"
            f"</tr>"
        )
    table = (
        "<style>"
        ".step-table td,.step-table th{border:1px solid #ddd;padding:6px;font-size:12px}"
        ".step-table{border-collapse:collapse;width:100%;margin:6px 0}"
        ".step-table th{background:#f4f4f4;text-align:left}"
        "</style>"
        "<h4>Execution Steps</h4>"
        "<table class='step-table'>"
        "<thead><tr><th>#</th><th>Step</th><th>Expected</th><th>Actual</th><th>Status</th><th>Time</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )

    extra = getattr(report, "extra", [])
    extra.append(html_extras.html(table))

    if report.failed:
        failed_step = next((s for s in reversed(steps) if s.status == "failed"), None)
        if failed_step:
            highlight = (
                f"<div style='padding:8px;border-left:4px solid #d33;background:#fdeaea'>"
                f"<strong>Failed at step:</strong> {failed_step.name}<br>"
                f"<strong>Expected:</strong> {failed_step.expected or '(none)'}<br>"
                f"<strong>Actual:</strong> {failed_step.actual or '(empty)'}"
                f"</div>"
            )
            extra.append(html_extras.html(highlight))

            try:
                if failed_step.screenshot_path and Path(failed_step.screenshot_path).exists():
                    with open(failed_step.screenshot_path, "rb") as img_file:
                        encoded = base64.b64encode(img_file.read()).decode("utf-8")
                    extra.append(html_extras.image(encoded, mime_type="image/png", extension="png", name="Screenshot"))
            except Exception as e:
                print(f"⚠️ Failed to embed screenshot: {e}")



    report.extra = extra

# ─────────────────────────────────────────────────────────────
# 📁 Save 'latest.html' and print path at end
# ─────────────────────────────────────────────────────────────
def _get_html_report_path(config) -> Path | None:
    try: return Path(config.option.htmlpath).resolve()
    except: return None

def _make_file_url(path: Path) -> str:
    return "file://" + quote(str(path))

def _latest_name_for(name: str) -> str:
    if "selenium_" in name: return "selenium_latest.html"
    if "test_suite_" in name: return "test_suite_latest.html"
    return "report_latest.html"

def pytest_sessionfinish(session, exitstatus):
    html_path = _get_html_report_path(session.config)
    if not html_path or not html_path.exists(): return
    latest = html_path.parent / _latest_name_for(html_path.name)
    try:
        shutil.copyfile(html_path, latest)
        idx = html_path.parent / "index.html"
        idx.write_text(
            "<!doctype html><html><head>"
            f"<meta http-equiv='refresh' content='0; url={latest.name}'></head>"
            "<body>Redirecting to "
            f"<a href='{latest.name}'>{latest.name}</a></body></html>",
            encoding="utf-8"
        )
    except: pass

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    html_path = _get_html_report_path(config)
    if not html_path: return
    url = _make_file_url(html_path)
    latest_url = _make_file_url(html_path.parent / _latest_name_for(html_path.name))
    terminalreporter.write_line(f"HTML report: {url}")
    terminalreporter.write_line(f"Latest copy: {latest_url}")