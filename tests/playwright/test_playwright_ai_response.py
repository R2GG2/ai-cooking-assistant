from playwright.sync_api import sync_playwright
import time
import pytest

# Original tests - superseded by new Page Object Model framework in test_functional_scenarios.py and test_ui_interactions.py
# These tests use a different approach and are kept for reference but skipped in favor of the new architecture
pytestmark = pytest.mark.skip(reason="Superseded by new POM framework tests")


def setup_browser(p):
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("http://127.0.0.1:5000")
    return browser, page


def test_ai_response():
    with sync_playwright() as p:
        browser, page = setup_browser(p)

        print("Filling in the question...")
        page.fill("#user-input", "I have chicken and carrots and an Instant Pot")
        time.sleep(2)

        print("Submitting the form...")
        page.click("input[type='submit']")
        page.wait_for_load_state("load")
        page.wait_for_selector("#ai-response", timeout=15000)

        response_text = page.inner_text("#ai-response")
        print("AI Response:", response_text)

        time.sleep(5)
        browser.close()


def test_allergy_response():
    with sync_playwright() as p:
        browser, page = setup_browser(p)

        print("Filling in allergy info...")
        page.fill("#user-input", "I'm allergic to peanuts")
        time.sleep(2)

        print("Submitting form...")
        page.click("input[type='submit']")
        page.wait_for_load_state("load")
        page.wait_for_selector("#ai-response", timeout=15000)

        response_text = page.inner_text("#ai-response")
        print("AI Response (allergy test):", response_text)

        assert (
            "avoid" in response_text.lower()
            or "allergy" in response_text.lower()
            or "peanut" in response_text.lower()
        )

        time.sleep(5)
        browser.close()


if __name__ == "__main__":
    test_ai_response()
    test_allergy_response()
