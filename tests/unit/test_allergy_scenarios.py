import pytest
import logging
from ai_app.response_logic import generate_response

logger = logging.getLogger(__name__)

# --- Restriction & Allergy-based tests ---
class TestRestrictionScenarios:
    # --- Simple restrictions ---
    @pytest.mark.parametrize("prompt", [
        "I am allergic to peanuts, suggest a dinner recipe",
        "No dairy please, I am lactose intolerant",
        "Avoid gluten, but I want bread alternatives",
        "I can't eat shellfish, give me something with chicken",
        "No pork, suggest a healthy dinner",
        "I want a vegan recipe without honey",
        "Make something sugar free with fruit",
    ])
    def test_common_restriction_prompts(self, prompt):
        """Ensure AI respects allergies and restrictions in responses."""
        logger.info(f"=== Testing Common Restriction: {prompt} ===")

        # Step 1: Send prompt to AI
        logger.info(f"Step 1: Sending prompt to AI: '{prompt}'")
        result = generate_response(prompt)

        # Step 2: Validate response type
        logger.info(f"Step 2: Validating response type (expected: str)")
        assert isinstance(result, str), f"Expected str, got {type(result)}"

        # Step 3: Check restriction is reflected in response
        logger.info(f"Step 3: Verifying restriction keywords in response")
        assert any(word in result.lower() for word in [
            "avoid", "without", "free", "substitute", "alternative", "restriction", "low-sugar"
        ]), f"Restriction not reflected in response: {result}"  # ✅ Updated to include "low-sugar"
        logger.info(f"✓ Test passed for restriction: {prompt[:50]}...")

    # --- Specific checks ---
    def test_peanut_allergy(self):
        logger.info("=== TC-ALLERGY-001: Peanut Allergy Test ===")
        logger.info("Step 1: Generating recipe avoiding peanuts")
        result = generate_response("Make a dessert but I am allergic to peanuts.")
        logger.info("Step 2: Verifying peanuts are not mentioned in recipe")
        assert "peanut" not in result.lower(), f"Peanut allergy not respected: {result}"
        logger.info("✓ Peanut allergy properly handled")

    def test_gluten_free(self):
        logger.info("=== TC-ALLERGY-002: Gluten-Free Test ===")
        logger.info("Step 1: Requesting gluten-free pasta suggestion")
        result = generate_response("Suggest pasta but gluten free.")
        logger.info("Step 2: Checking for gluten-free alternatives in response")
        assert "gluten" in result.lower() or "alternative" in result.lower(), \
            f"Expected gluten-free option: {result}"
        logger.info("✓ Gluten-free requirement acknowledged")

    def test_dairy_free(self):
        logger.info("=== TC-ALLERGY-003: Dairy-Free Test ===")
        logger.info("Step 1: Requesting creamy soup without dairy")
        result = generate_response("Make a creamy soup without dairy.")
        logger.info("Step 2: Verifying dairy alternatives are mentioned")
        assert "dairy" in result.lower() or "substitute" in result.lower(), \
            f"Expected dairy restriction mention: {result}"
        logger.info("✓ Dairy restriction properly handled")

    def test_religious_restriction(self):
        logger.info("=== TC-ALLERGY-004: Religious Restriction (No Pork) ===")
        logger.info("Step 1: Requesting meal without pork")
        result = generate_response("Suggest a meal but avoid pork.")
        logger.info("Step 2: Ensuring pork is not included in suggestion")
        assert "pork" not in result.lower(), f"Pork restriction not respected: {result}"
        logger.info("✓ Religious restriction respected")

    # --- Complex multi-axis cases ---
    @pytest.mark.parametrize("prompt", [
        "Instant Pot recipe with chicken and potatoes, no dairy",
        "Gluten-free vegan pasta dish",
        "Slow cooker stew without beef or pork",
        "Low-carb (keto) dinner, no dairy, use fish",
        "Quick stovetop recipe without nuts",
        "Vegetarian but also gluten free, using quinoa",
    ])
    def test_multi_axis_prompts(self, prompt):
        """Ensure AI handles combined restrictions and cooking styles."""
        logger.info(f"=== Testing Multi-Axis Prompt: {prompt} ===")
        logger.info(f"Step 1: Sending complex multi-restriction prompt")
        result = generate_response(prompt)
        logger.info(f"Step 2: Validating response type")
        assert isinstance(result, str)
        logger.info(f"Step 3: Verifying all restrictions are respected")
        assert not any(forbidden in result.lower() for forbidden in [
            "pork", "beef", "dairy", "peanut"
        ] if forbidden in prompt.lower()), f"Restriction violated: {result}"
        logger.info(f"✓ Multi-axis restrictions handled correctly")

    # --- Ambiguous or edge prompts ---
    @pytest.mark.parametrize("prompt", [
        "I don't like sugar but I want dessert",
        "Make something creamy but lactose free",
        "Suggest a traditional dish without cultural bias",
        "Healthy dinner but no carbs (clarify if needed)",
    ])
    def test_ambiguous_cases(self, prompt):
        """Check that AI provides safe, clarifying or alternative suggestions."""
        logger.info(f"=== Testing Ambiguous Case: {prompt} ===")
        logger.info(f"Step 1: Sending ambiguous prompt to AI")
        result = generate_response(prompt)
        logger.info(f"Step 2: Validating response provides alternatives")
        assert isinstance(result, str)
        logger.info(f"Step 3: Checking for helpful keywords in response")
        assert any(word in result.lower() for word in [
            "alternative", "option", "without", "free", "substitute"
        ]), f"Ambiguous case not handled well: {result}"
        logger.info(f"✓ Ambiguous case handled with helpful suggestions")
