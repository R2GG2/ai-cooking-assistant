import pytest
from ai_app.response_logic import generate_response

# --- Ingredient-based tests ---
class TestIngredientScenarios:
    @pytest.mark.parametrize("prompt", [
        "I have fish and lemon",
        "Can I cook beef with garlic?",
        "Make something with rice and beans",
        "What if I only have bread?",
        "I have chicken, potatoes, and carrots",
        "Make a meal with salmon, dill, and lemon",
        "I only have pasta, tomato sauce, and cheese",
        "Cook with eggs and spinach",
        "What can I make with mushrooms and soy sauce?",
        "Give me a recipe using turkey and cranberries",
    ])
    def test_basic_ingredient_prompts(self, prompt):
        result = generate_response(prompt)
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert any(word in result.lower() for word in ["dish", "cook", "recipe", "meal", "suggest"]), \
            f"Unexpected response for '{prompt}': {result}"

    def test_chicken_and_rice(self):
        result = generate_response("I have chicken and rice.")
        assert any(word in result.lower() for word in ["chicken", "rice", "dish", "recipe"]), \
            f"Unexpected response: {result}"

    def test_chicken_lemon_parsley(self):
        result = generate_response("I want to cook chicken with lemon and parsley.")
        for ingredient in ["chicken", "lemon", "parsley"]:
            assert ingredient in result.lower(), f"Missing '{ingredient}' in response: {result}"

    def test_empty_ingredient_list(self):
        result = generate_response("I don’t know what I have.")
        assert "suggest" in result.lower() or "idea" in result.lower(), \
            f"Expected a fallback suggestion, got: {result}"

    def test_gibberish_input(self):
        result = generate_response("asdfghjkl qwertyuiop zxcvbnm")
        assert isinstance(result, str) and len(result) > 0, \
            f"Unexpected response to gibberish: {result}"

    # --- Extra: ingredient + restriction scenarios ---
    def test_chicken_with_gluten_restriction(self):
        result = generate_response("I want to make chicken soup but I can't have gluten.")
        assert "gluten" in result.lower() or "avoid" in result.lower(), \
            f"Expected gluten restriction handling, got: {result}"

    def test_fish_with_dairy_free(self):
        result = generate_response("Give me a dairy-free recipe with fish and herbs.")
        assert "dairy" in result.lower() or "avoid" in result.lower() or "free" in result.lower(), \
            f"Expected dairy-free handling, got: {result}"

    def test_pork_and_chicken_conflict(self):
        result = generate_response("Can I cook chicken and pork together?")
        assert "avoid" in result.lower() or "cannot" in result.lower() or "suggest" in result.lower(), \
            f"Expected restriction/conflict handling, got: {result}"

    def test_low_sugar_meal(self):
        result = generate_response("Suggest a low-sugar dessert with apples.")
        assert "low-sugar" in result.lower() or "avoid" in result.lower() or "healthy" in result.lower(), \
            f"Expected sugar restriction handling, got: {result}"
