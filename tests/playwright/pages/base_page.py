"""
Base Page Object - provides common functionality for all page objects.
Demonstrates Page Object Model (POM) architecture best practices.
"""
from playwright.sync_api import Page, expect


class BasePage:
    """Base page class that all page objects inherit from."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        """Navigate to a URL."""
        self.page.goto(url)

    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()

    def wait_for_load(self):
        """Wait for page to finish loading."""
        self.page.wait_for_load_state("load")

    def take_screenshot(self, name: str):
        """Take a screenshot of the current page."""
        self.page.screenshot(path=f"screenshots/{name}.png")

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is visible on the page."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except:
            return False

    def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        return self.page.inner_text(selector)

    def click(self, selector: str):
        """Click an element."""
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """Fill in a form field."""
        self.page.fill(selector, text)

    def wait_for_selector(self, selector: str, timeout: int = 10000):
        """Wait for a selector to appear."""
        self.page.wait_for_selector(selector, timeout=timeout)
