import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    yield driver
    driver.quit()

def test_search_input(driver):
    # Open the test page
    driver.get(f"{BASE_URL}/test_page.html")

    # Find the search box and type query
    search_box = driver.find_element(By.ID, "user-input")
    search_box.send_keys("AI QA automation with Python")
    search_box.send_keys(Keys.RETURN)

    # Wait for the result (make sure the element is still interactable)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "user-input"))
    )

    # Optional: Take a screenshot
    driver.save_screenshot("selenium_tests/search_results.png")
