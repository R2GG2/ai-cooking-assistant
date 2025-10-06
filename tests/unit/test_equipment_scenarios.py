import pytest
from ai_app.response_logic import generate_response


# --- Equipment & Cooking Method-based tests ---
class TestEquipmentScenarios:
    @pytest.mark.parametrize("prompt", [
        "I want to cook chicken in the Instant Pot",
        "Make beef stew with a slow cooker",
        "Can I bake salmon in the oven?",
        "What can I make on the stovetop with pasta?",
        "Suggest a grilled dish with vegetables",
        "Can I make fries in the air fryer?",
        "Use a wok for stir fry with beef and broccoli",
        "Microwave a quick snack with eggs",
    ])
    def test_common_equipment_prompts(self, prompt):
        result = generate_response(prompt)
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert any(word in result.lower() for word in [
            "instant pot", "slow cooker", "oven", "stovetop", "grill",
            "air fryer", "wok", "microwave", "cook", "recipe"
        ]), f"Unexpected response for '{prompt}': {result}"

    def test_instant_pot_chicken_rice(self):
        result = generate_response("Make chicken and rice in the Instant Pot.")
        assert "instant pot" in result.lower(), f"Expected Instant Pot mention, got: {result}"

    def test_slow_cooker_soup(self):
        result = generate_response("I want a soup in my slow cooker with beans and veggies.")
        assert "slow cooker" in result.lower(), f"Expected slow cooker mention, got: {result}"

    def test_oven_bake_conflict(self):
        result = generate_response("Can I fry salmon in the oven?")
        assert "oven" in result.lower() and ("bake" in result.lower() or "roast" in result.lower()), \
            f"Expected oven-safe correction, got: {result}"

    def test_air_fryer_dessert(self):
        result = generate_response("Make a dessert in the air fryer with apples.")
        assert "air fryer" in result.lower(), f"Expected air fryer mention, got: {result}"

    def test_wok_stirfry(self):
        result = generate_response("Stir fry noodles in a wok with shrimp.")
        assert "wok" in result.lower() or "stir" in result.lower(), \
            f"Expected wok-based cooking, got: {result}"

    def test_microwave_restriction(self):
        result = generate_response("Microwave mac and cheese without dairy.")
        assert "microwave" in result.lower(), f"Expected microwave mention, got: {result}"
        assert "dairy" in result.lower() or "avoid" in result.lower(), \
            f"Expected dairy restriction handling, got: {result}"
