# selenium_tests/google_search_test.py
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    yield driver
    driver.quit()

def test_search_input(step, driver):
    """Search input echoes text into the AI response area on submit."""
    message = "AI QA automation with Python"

    # Step 1: Open the page and see input
    with step("Open test page", expected="Input box is visible", driver=driver) as s:
        driver.get(f"{BASE_URL}/test_page.html")
        box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-input"))
        )
        s.actual = f"title='{driver.title}', input_displayed={box.is_displayed()}"
        assert box.is_displayed(), "Expected #user-input to be visible"

    # Step 2: Type message
    with step("Enter text", expected=f"Input value is '{message}'", driver=driver) as s:
        box = driver.find_element(By.ID, "user-input")
        box.clear()
        box.send_keys(message)
        s.actual = f"value='{box.get_attribute('value')}'"
        assert box.get_attribute("value") == message

    # Step 3: Submit and verify echo
    with step("Submit form", expected="AI echoes the same message", driver=driver) as s:
        driver.find_element(By.ID, "send-btn").click()
        
        # Wait until #ai-response has non-empty text
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "ai-response").text.strip() != ""
        )
        
        resp_text = driver.find_element(By.ID, "ai-response").text.strip()
        s.actual = f"ai-response='{resp_text}'"
        expected_keywords = ["allergies", "ingredients", "dish", "recipe", "cook"]
        assert any(k in resp_text.lower() for k in expected_keywords), \
            f"Unexpected AI response: {resp_text}"