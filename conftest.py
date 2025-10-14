import os
import sys
import pathlib
import pytest
from dotenv import load_dotenv
import subprocess
import time
import signal
import json
from datetime import datetime
from pathlib import Path

# ---- Load environment early (BASE_URL, etc.) ----
load_dotenv()

# ---- Make ./src importable for tests ----
ROOT = pathlib.Path(__file__).parent.resolve()
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

print("PYTHONPATH:", sys.path)

# ---- Optional: base URL fixture for UI tests ----
@pytest.fixture(scope="session")
def base_url():
    """Base URL for UI tests; set BASE_URL in .env to override."""
    return os.getenv("BASE_URL", "http://127.0.0.1:5000")

# ---- Selenium WebDriver fixture (Chrome) ----
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="session")
def driver():
    """Session-scoped Chrome driver managed by webdriver-manager."""
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )
    yield driver
    driver.quit()

# ---- Auto-start Flask server for UI tests ----
@pytest.fixture(scope="session", autouse=True)
def flask_app():
    """Automatically start the Flask app for testing."""
    project_root = pathlib.Path("/Users/ginka/Documents/ai-cooking-assistant")
    app_path = project_root / "ai_app" / "app.py"
    log_path = project_root / "tests" / "selenium" / "reports" / "flask_server.log"

    print(f"\n[conftest] Starting Flask app from {app_path}...")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    flask_process = subprocess.Popen(
        ["python", str(app_path)],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
        cwd=str(project_root)
    )

    time.sleep(2)

    if flask_process.poll() is not None:
        raise RuntimeError(f"Flask exited early. Logs: {log_path}")

    yield

    print("\n[conftest] Stopping Flask app...")
    os.killpg(os.getpgid(flask_process.pid), signal.SIGTERM)
    flask_process.wait()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test results and append structured logs to a JSON file."""
    outcome = yield
    result = outcome.get_result()

    # Only log call phase (skip setup/teardown)
    if result.when != "call":
        return

    log_entry = {
        "test_name": item.name,
        "node_id": item.nodeid,
        "outcome": result.outcome.upper(),
        "duration_sec": round(result.duration, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "response_excerpt": getattr(item, "response_excerpt", None),
    }

    log_file = Path("test_results_json") / "test_feedback.json"
    log_file.parent.mkdir(exist_ok=True)

    # Append (or create file if missing)
    if log_file.exists():
        with open(log_file, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(log_entry)
            f.seek(0)
            json.dump(data, f, indent=2)
    else:
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump([log_entry], f, indent=2)

    print(f"\n[LOGGED] {item.name} → {result.outcome.upper()}")
