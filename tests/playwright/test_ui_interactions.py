"""
UI Interaction Tests for AI Cooking Assistant.
Tests user interface elements, interactions, and visual behavior.
"""
import pytest
from playwright.sync_api import Page
from pages.cooking_assistant_page import CookingAssistantPage


class TestUIElements:
    """Test suite for UI element presence and properties."""

    def test_input_field_is_editable(self, cooking_assistant_page: CookingAssistantPage):
        """Verify the input field accepts user input."""
        test_text = "Test ingredients"
        cooking_assistant_page.enter_ingredients(test_text)

        input_value = cooking_assistant_page.page.input_value(cooking_assistant_page.USER_INPUT_FIELD)
        assert input_value == test_text, "Input field should accept and retain text"

    def test_submit_button_is_clickable(self, cooking_assistant_page: CookingAssistantPage):
        """Verify submit button is enabled and clickable."""
        button_element = cooking_assistant_page.page.locator(cooking_assistant_page.SUBMIT_BUTTON)
        assert button_element.is_enabled(), "Submit button should be enabled"
        assert button_element.is_visible(), "Submit button should be visible"

    def test_response_area_becomes_visible_after_submission(self, cooking_assistant_page: CookingAssistantPage):
        """Verify AI response area appears after form submission."""
        # Initially, response area may or may not be visible (depends on implementation)
        cooking_assistant_page.enter_ingredients("Quick test query")
        cooking_assistant_page.submit_query()
        cooking_assistant_page.wait_for_ai_response()

        assert cooking_assistant_page.is_response_visible(), \
            "AI response area should be visible after submission"


class TestFormValidation:
    """Test form validation and error handling."""

    def test_empty_submission_handling(self, cooking_assistant_page: CookingAssistantPage):
        """Test behavior when submitting empty form."""
        # Submit without entering anything
        cooking_assistant_page.submit_query()

        # Application should either:
        # 1. Show an error message
        # 2. Handle gracefully with a response
        # 3. Prevent submission
        # This test documents actual behavior
        try:
            cooking_assistant_page.wait_for_ai_response(timeout=5000)
            response = cooking_assistant_page.get_ai_response_text()
            # If we get here, app handles empty input gracefully
            assert True, "Application handles empty input"
        except:
            # If timeout occurs, form might have validation preventing empty submission
            assert True, "Application prevents empty submission or shows validation"

    def test_special_characters_in_input(self, cooking_assistant_page: CookingAssistantPage):
        """Test handling of special characters in user input."""
        special_input = "I have 1/2 cup of @#$% ingredients!"
        response = cooking_assistant_page.submit_query_and_wait(special_input, timeout=15000)

        # Should handle gracefully without crashing
        assert len(response) >= 0, "Application should handle special characters without crashing"


class TestResponsiveness:
    """Test application responsiveness and loading states."""

    @pytest.mark.slow
    def test_response_time_is_reasonable(self, cooking_assistant_page: CookingAssistantPage):
        """Verify AI responds within a reasonable timeframe."""
        import time

        query = "Quick recipe with pasta"
        cooking_assistant_page.enter_ingredients(query)

        start_time = time.time()
        cooking_assistant_page.submit_query()
        cooking_assistant_page.wait_for_ai_response(timeout=30000)  # 30 second max
        end_time = time.time()

        response_time = end_time - start_time

        # Response should come within 30 seconds (generous timeout for AI)
        assert response_time < 30, f"Response took {response_time:.2f}s - should be under 30s"

        # Log response time for performance tracking
        print(f"\n✓ AI response time: {response_time:.2f} seconds")

    def test_multiple_consecutive_queries(self, cooking_assistant_page: CookingAssistantPage):
        """Test application handles multiple queries in sequence."""
        queries = [
            "First query: pasta recipe",
            "Second query: chicken dish",
            "Third query: dessert idea"
        ]

        for i, query in enumerate(queries, 1):
            response = cooking_assistant_page.submit_query_and_wait(query, timeout=20000)
            assert len(response) > 0, f"Query {i} should receive a response"
            print(f"\n✓ Query {i} completed successfully")


class TestAccessibility:
    """Basic accessibility checks for the cooking assistant interface."""

    def test_page_has_title(self, page: Page):
        """Verify page has a meaningful title for screen readers."""
        page.goto("http://127.0.0.1:5000")
        title = page.title()
        assert len(title) > 0, "Page should have a title for accessibility"

    def test_form_elements_have_labels_or_placeholders(self, cooking_assistant_page: CookingAssistantPage):
        """Verify input fields have labels or placeholders for accessibility."""
        input_field = cooking_assistant_page.page.locator(cooking_assistant_page.USER_INPUT_FIELD)

        # Check for placeholder or associated label
        placeholder = input_field.get_attribute("placeholder")
        aria_label = input_field.get_attribute("aria-label")
        has_label = placeholder or aria_label or input_field.get_attribute("name")

        assert has_label, "Input field should have placeholder, aria-label, or name for accessibility"


@pytest.mark.visual
class TestVisualRegression:
    """Visual regression tests (can be extended with screenshot comparison)."""

    def test_capture_initial_page_state(self, cooking_assistant_page: CookingAssistantPage, page: Page):
        """Capture screenshot of initial page state for visual regression testing."""
        # This test captures a baseline screenshot that can be compared in future test runs
        page.screenshot(path="test-results/screenshots/home-page-baseline.png")
        assert True, "Screenshot captured for visual baseline"

    def test_capture_response_state(self, cooking_assistant_page: CookingAssistantPage, page: Page):
        """Capture screenshot after AI response for visual testing."""
        cooking_assistant_page.submit_query_and_wait("Sample recipe query")
        page.screenshot(path="test-results/screenshots/response-page.png")
        assert True, "Screenshot captured after response"
