import os
import sys
import pathlib
import pytest
from dotenv import load_dotenv

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
    # Run headless in CI or when HEADLESS=1 in env
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
