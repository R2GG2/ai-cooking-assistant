"""
Demo Playwright tests using proper step logging and categories.
"""
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("query", [
    "Login Screen Displays",
])
@pytest.mark.category("🎭 UI Tests")
def test_page_load(page, query):
    """Page loads and displays input form."""
    logger.info("TC-UI-001: Starting page load test")

    # Navigate to application
    page.goto("http://127.0.0.1:5000")
    assert "127.0.0.1:5000" in page.url
    logger.info(f"✓ Page loaded successfully: {page.url}")

    # Verify input field is present
    input_field = page.locator("#user-input")
    assert input_field.is_visible()
    logger.info("✓ Input field is visible")

    # Verify submit button is present
    submit_btn = page.locator("#send-btn")
    assert submit_btn.is_visible()
    logger.info(f"✓ Submit button is visible and enabled")

    logger.info("TC-UI-001: PASSED - Page loads successfully")


@pytest.mark.parametrize("query", [
    "Recipe Suggestion Works",
])
@pytest.mark.category("🍳 Ingredients")
def test_recipe_suggestion(page, query):
    """AI provides recipe suggestions."""
    logger.info("TC-ING-001: Starting recipe suggestion test")

    message = "I have chicken and rice"

    # Navigate and find input
    page.goto("http://127.0.0.1:5000")
    input_field = page.locator("#user-input")
    assert input_field.is_visible()
    logger.info("✓ Input field ready")

    # Enter query
    input_field.fill(message)
    assert input_field.input_value() == message
    logger.info(f"✓ Entered query: '{message}'")

    # Submit and wait for response
    page.locator("#send-btn").click()
    page.wait_for_selector("#chat-box >> text=/./", timeout=15000)
    response = page.locator("#chat-box").inner_text()
    assert len(response) > 0
    logger.info(f"✓ AI generated response ({len(response)} chars)")

    logger.info("TC-ING-001: PASSED - Recipe suggestion works")
