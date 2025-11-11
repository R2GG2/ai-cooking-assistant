"""
Cooking Assistant Page Object.
Encapsulates all interactions with the AI Cooking Assistant interface.
"""
from playwright.sync_api import Page
from .base_page import BasePage


class CookingAssistantPage(BasePage):
    """Page object for the AI Cooking Assistant application."""

    # Locators
    USER_INPUT_FIELD = "#user-input"
    SUBMIT_BUTTON = "#send-btn"  # Updated to match actual HTML
    AI_RESPONSE_AREA = "#chat-box"  # Updated to match actual HTML

    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:5000"):
        super().__init__(page)
        self.base_url = base_url

    def navigate(self):
        """Navigate to the cooking assistant page."""
        self.navigate_to(self.base_url)
        self.wait_for_load()

    def enter_ingredients(self, ingredients: str):
        """Enter ingredients or cooking query into the input field."""
        self.fill(self.USER_INPUT_FIELD, ingredients)

    def submit_query(self):
        """Submit the cooking query."""
        self.click(self.SUBMIT_BUTTON)
        self.wait_for_load()

    def wait_for_ai_response(self, timeout: int = 15000):
        """Wait for AI response to appear."""
        self.wait_for_selector(self.AI_RESPONSE_AREA, timeout=timeout)

    def get_ai_response_text(self) -> str:
        """Get the AI response text."""
        return self.get_text(self.AI_RESPONSE_AREA)

    def is_response_visible(self) -> bool:
        """Check if AI response area is visible."""
        return self.is_element_visible(self.AI_RESPONSE_AREA)

    def submit_query_and_wait(self, ingredients: str, timeout: int = 15000) -> str:
        """
        Complete workflow: enter ingredients, submit, wait for response, return response.
        This is a convenience method that combines multiple actions.
        """
        self.enter_ingredients(ingredients)
        self.submit_query()
        self.wait_for_ai_response(timeout)
        return self.get_ai_response_text()

    def verify_response_contains_keywords(self, response: str, keywords: list) -> bool:
        """
        Verify that the AI response contains at least one of the expected keywords.
        Useful for testing that AI understands the query context.
        """
        response_lower = response.lower()
        return any(keyword.lower() in response_lower for keyword in keywords)
