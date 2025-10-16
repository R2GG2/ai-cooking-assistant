import pytest
from ai_app.response_logic import generate_response

# --- Restriction & Allergy-based tests ---
class TestRestrictionScenarios:
    # --- Simple restrictions ---
    @pytest.mark.parametrize("prompt", [
        "I am allergic to peanuts, suggest a dinner recipe",
        "No dairy please, I am lactose intolerant",
        "Avoid gluten, but I want bread alternatives",
        "I can’t eat shellfish, give me something with chicken",
        "No pork, suggest a healthy dinner",
        "I want a vegan recipe without honey",
        "Make something sugar free with fruit",
    ])
    def test_common_restriction_prompts(self, prompt):
        """Ensure AI respects allergies and restrictions in responses."""
        result = generate_response(prompt)
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert any(word in result.lower() for word in [
            "avoid", "without", "free", "substitute", "alternative", "restriction", "low-sugar"
        ]), f"Restriction not reflected in response: {result}"  # ✅ Updated to include "low-sugar"

    # --- Specific checks ---
    def test_peanut_allergy(self):
        result = generate_response("Make a dessert but I am allergic to peanuts.")
        assert "peanut" not in result.lower(), f"Peanut allergy not respected: {result}"

    def test_gluten_free(self):
        result = generate_response("Suggest pasta but gluten free.")
        assert "gluten" in result.lower() or "alternative" in result.lower(), \
            f"Expected gluten-free option: {result}"

    def test_dairy_free(self):
        result = generate_response("Make a creamy soup without dairy.")
        assert "dairy" in result.lower() or "substitute" in result.lower(), \
            f"Expected dairy restriction mention: {result}"

    def test_religious_restriction(self):
        result = generate_response("Suggest a meal but avoid pork.")
        assert "pork" not in result.lower(), f"Pork restriction not respected: {result}"

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
        result = generate_response(prompt)
        assert isinstance(result, str)
        assert not any(forbidden in result.lower() for forbidden in [
            "pork", "beef", "dairy", "peanut"
        ] if forbidden in prompt.lower()), f"Restriction violated: {result}"

    # --- Ambiguous or edge prompts ---
    @pytest.mark.parametrize("prompt", [
        "I don’t like sugar but I want dessert",
        "Make something creamy but lactose free",
        "Suggest a traditional dish without cultural bias",
        "Healthy dinner but no carbs (clarify if needed)",
    ])
    def test_ambiguous_cases(self, prompt):
        """Check that AI provides safe, clarifying or alternative suggestions."""
        result = generate_response(prompt)
        assert isinstance(result, str)
        assert any(word in result.lower() for word in [
            "alternative", "option", "without", "free", "substitute"
        ]), f"Ambiguous case not handled well: {result}"
