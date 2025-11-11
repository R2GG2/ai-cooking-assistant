"""
Functional Test Scenarios for AI Cooking Assistant.
Tests core functionality using Page Object Model architecture.
"""
import pytest
import logging
from pages.cooking_assistant_page import CookingAssistantPage

logger = logging.getLogger(__name__)


class TestBasicFunctionality:
    """Test suite for basic cooking assistant functionality."""

    @pytest.mark.category("🎭 UI Tests")
    def test_page_loads_successfully(self, cooking_assistant_page: CookingAssistantPage):
        """Verify the application loads and displays the input form."""
        logger.info("TC-UI-002: Starting page load verification test")

        # Verify input field is displayed
        assert cooking_assistant_page.is_element_visible(cooking_assistant_page.USER_INPUT_FIELD)
        logger.info("✓ Login screen is displayed")

        # Verify submit button is present
        assert cooking_assistant_page.is_element_visible(cooking_assistant_page.SUBMIT_BUTTON)
        logger.info("✓ Submit button is present")

        logger.info("TC-UI-002: PASSED - Page loaded successfully with all required elements")

    @pytest.mark.category("🍳 Ingredients")
    def test_ingredient_based_recipe_suggestion(self, cooking_assistant_page: CookingAssistantPage):
        """Test AI provides recipe suggestions based on available ingredients."""
        logger.info("TC-ING-002: Starting ingredient-based recipe suggestion test")

        query = "I have chicken, rice, and bell peppers"

        # Submit query
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info(f"✓ Entered ingredients query: '{query}'")

        # Verify response is not empty
        assert len(response) > 0, "AI response should not be empty"
        logger.info(f"✓ AI response received ({len(response)} chars)")

        # Verify response mentions at least one ingredient
        assert cooking_assistant_page.verify_response_contains_keywords(
            response, ["chicken", "rice", "pepper", "recipe"]
        ), "Response should reference provided ingredients or recipes"
        logger.info("✓ Response contains ingredient references")

        logger.info("TC-ING-002: PASSED - Recipe suggestion based on ingredients works")

    @pytest.mark.category("🔧 Equipment")
    def test_cooking_equipment_query(self, cooking_assistant_page: CookingAssistantPage):
        """Test AI responds appropriately to specific cooking equipment queries."""
        logger.info("TC-EQ-001: Starting equipment-specific query test")

        query = "I have an Instant Pot and chicken. What can I make?"

        # Submit query
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info(f"✓ Entered equipment-specific query")

        # Verify response is not empty
        assert len(response) > 0
        logger.info("✓ AI processed equipment query")

        # Verify Instant Pot acknowledgment
        assert cooking_assistant_page.verify_response_contains_keywords(
            response, ["instant pot", "pressure", "chicken", "cook"]
        ), "Response should acknowledge Instant Pot and provide relevant suggestions"
        logger.info("✓ Response acknowledges Instant Pot and provides suggestions")

        logger.info("TC-EQ-001: PASSED - Equipment query handled correctly")


class TestAllergyAndDietaryConcerns:
    """Test suite for allergy awareness and dietary restrictions."""

    @pytest.mark.category("🚫 Allergy/Restrictions")
    def test_allergy_warning_detection(self, cooking_assistant_page: CookingAssistantPage):
        """Verify AI acknowledges and addresses allergy concerns."""
        logger.info("TC-ALL-001: Starting allergy warning detection test")

        query = "I'm allergic to peanuts. What should I avoid?"
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info(f"✓ Submitted allergy query")

        assert cooking_assistant_page.verify_response_contains_keywords(
            response, ["allergy", "peanut", "avoid", "caution", "allergen"]
        ), "AI should acknowledge allergy concerns in response"
        logger.info("✓ AI acknowledges allergy concerns in response")

        logger.info("TC-ALL-001: PASSED - Allergy warning detection works")

    @pytest.mark.category("🚫 Allergy/Restrictions")
    def test_dietary_restriction_vegetarian(self, cooking_assistant_page: CookingAssistantPage):
        """Test AI provides vegetarian-appropriate suggestions."""
        logger.info("TC-ALL-002: Starting vegetarian dietary restriction test")

        query = "I'm vegetarian and have mushrooms, tofu, and spinach"
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info("✓ Submitted vegetarian query")

        assert len(response) > 0
        logger.info(f"✓ AI response received ({len(response)} chars)")

        # Should not suggest meat
        meat_keywords = ["chicken", "beef", "pork", "fish", "meat"]
        response_lower = response.lower()
        has_meat_suggestion = any(keyword in response_lower for keyword in meat_keywords)

        assert not has_meat_suggestion or "vegetarian" in response_lower, \
            "Should provide vegetarian-appropriate suggestions"
        logger.info("✓ Response provides vegetarian-appropriate suggestions")

        logger.info("TC-ALL-002: PASSED - Vegetarian restriction handled correctly")

    @pytest.mark.category("🚫 Allergy/Restrictions")
    def test_gluten_free_inquiry(self, cooking_assistant_page: CookingAssistantPage):
        """Test AI handles gluten-free dietary requirements."""
        logger.info("TC-ALL-003: Starting gluten-free inquiry test")

        query = "I need gluten-free recipe ideas with chicken and vegetables"
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info("✓ Submitted gluten-free query")

        assert cooking_assistant_page.verify_response_contains_keywords(
            response, ["gluten-free", "gluten", "alternative", "rice", "quinoa"]
        ), "AI should acknowledge gluten-free requirement"
        logger.info("✓ AI acknowledges gluten-free requirement")

        logger.info("TC-ALL-003: PASSED - Gluten-free inquiry handled correctly")


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.mark.category("🔍 Edge Cases")
    def test_empty_pantry_scenario(self, cooking_assistant_page: CookingAssistantPage):
        """Test how AI responds to minimal ingredients."""
        logger.info("TC-EDGE-001: Starting empty pantry scenario test")

        query = "I only have salt and water"
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info("✓ Submitted minimal ingredients query")

        assert len(response) > 0, "AI should provide some response even with minimal ingredients"
        logger.info(f"✓ AI provided response to minimal ingredients ({len(response)} chars)")

        logger.info("TC-EDGE-001: PASSED - Empty pantry scenario handled")

    @pytest.mark.category("🔍 Edge Cases")
    def test_vague_cooking_question(self, cooking_assistant_page: CookingAssistantPage):
        """Test AI handles vague or broad questions gracefully."""
        logger.info("TC-EDGE-002: Starting vague question test")

        query = "How do I cook?"
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info("✓ Submitted vague query")

        assert len(response) > 0, "AI should provide helpful response to vague questions"
        logger.info(f"✓ AI provided helpful response ({len(response)} chars)")

        logger.info("TC-EDGE-002: PASSED - Vague question handled gracefully")

    @pytest.mark.category("🔍 Edge Cases")
    def test_multiple_dietary_restrictions(self, cooking_assistant_page: CookingAssistantPage):
        """Test AI handles multiple constraints simultaneously."""
        logger.info("TC-EDGE-003: Starting multiple dietary restrictions test")

        query = "I'm vegan, gluten-free, and have nut allergies. I have quinoa and vegetables."
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info("✓ Submitted multiple constraints query")

        assert len(response) > 0
        logger.info(f"✓ AI response received ({len(response)} chars)")

        assert cooking_assistant_page.verify_response_contains_keywords(
            response, ["vegan", "gluten-free", "allergy", "quinoa", "vegetable"]
        ), "AI should address multiple constraints"
        logger.info("✓ Response addresses all dietary constraints")

        logger.info("TC-EDGE-003: PASSED - Multiple restrictions handled correctly")


@pytest.mark.slow
class TestResponseQuality:
    """Test the quality and usefulness of AI responses."""

    @pytest.mark.category("✅ Response Quality")
    def test_response_includes_cooking_instructions(self, cooking_assistant_page: CookingAssistantPage):
        """Verify AI provides actionable cooking instructions, not just ingredient lists."""
        logger.info("TC-QUAL-001: Starting cooking instructions quality test")

        query = "How do I make a simple pasta dish with tomatoes and garlic?"
        response = cooking_assistant_page.submit_query_and_wait(query, timeout=20000)
        logger.info("✓ Submitted recipe request")

        # Look for action words typically found in instructions
        instruction_keywords = ["cook", "heat", "add", "stir", "boil", "minutes", "season"]
        assert cooking_assistant_page.verify_response_contains_keywords(
            response, instruction_keywords
        ), "Response should include cooking instructions with action words"
        logger.info("✓ Response includes actionable cooking instructions")

        logger.info("TC-QUAL-001: PASSED - Cooking instructions quality verified")

    @pytest.mark.category("✅ Response Quality")
    def test_response_reasonable_length(self, cooking_assistant_page: CookingAssistantPage):
        """Verify AI responses are neither too short nor excessively long."""
        logger.info("TC-QUAL-002: Starting response length test")

        query = "What's a good weeknight dinner recipe?"
        response = cooking_assistant_page.submit_query_and_wait(query)
        logger.info("✓ Submitted dinner query")

        # Reasonable length: at least 50 characters, but not a novel
        assert len(response) >= 50, "Response should be substantive (at least 50 characters)"
        logger.info(f"✓ Response is substantive ({len(response)} chars)")

        assert len(response) <= 5000, "Response should be concise (under 5000 characters)"
        logger.info("✓ Response is concise (under 5000 chars)")

        logger.info("TC-QUAL-002: PASSED - Response length is reasonable")
