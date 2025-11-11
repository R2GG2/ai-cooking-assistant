"""
Playwright test configuration and fixtures.
Provides reusable test setup for all Playwright tests.
"""
import pytest
from playwright.sync_api import sync_playwright, Browser, Page, Playwright
from pages.cooking_assistant_page import CookingAssistantPage

# Note: Report hooks registered in root conftest.py to avoid conflicts


@pytest.fixture(scope="session")
def playwright_instance():
    """Create a Playwright instance for the test session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    """
    Create a browser instance for the test session.
    Uses Chromium by default in headless mode.
    """
    browser = playwright_instance.chromium.launch(
        headless=True,  # Run in background without opening browser window
        # slow_mo=500  # Only needed for visual debugging
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser) -> Page:
    """Create a new page for each test function."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        record_video_dir="test-results/videos" if False else None  # Enable for video recording
    )
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture(scope="function")
def cooking_assistant_page(page: Page) -> CookingAssistantPage:
    """
    Provide a Cooking Assistant Page Object for tests.
    Navigates to the application automatically.
    """
    assistant_page = CookingAssistantPage(page)
    assistant_page.navigate()
    return assistant_page


@pytest.fixture
def step(request):
    """
    Step-by-step test logging for beautiful reports.
    Usage: with step("Step description", expected="Expected result", driver=page) as s:
               s.actual = "Actual result"
    """
    from contextlib import ContextDecorator
    from datetime import datetime
    from pathlib import Path
    import html

    SCREEN_DIR = Path(__file__).parent / "reports" / "screenshots"
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)

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
                    self.driver.screenshot(path=str(path))
                    self.screenshot_path = path
                except: pass
            return False

    def _make(name, expected="", driver=None):
        return Step(request, name, expected, driver)
    return _make


# Inject step details into HTML report
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    from pytest_html import extras as html_extras
    import base64
    from pathlib import Path

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
        if failed_step and failed_step.screenshot_path and Path(failed_step.screenshot_path).exists():
            try:
                with open(failed_step.screenshot_path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode("utf-8")
                extra.append(html_extras.image(encoded, mime_type="image/png", extension="png", name="Screenshot"))
            except: pass

    report.extra = extra
