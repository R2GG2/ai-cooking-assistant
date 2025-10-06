import pytest
from ai_app.response_logic import generate_response

@pytest.mark.parametrize("prompt", [
    "I have fish and lemon",
    "Can I cook beef with garlic?",
    "Make something with rice and beans",
    "What if I only have bread?",
])
def test_additional_ingredient_scenarios(prompt):
    """Ensure AI produces recipe-like guidance for varied ingredients."""
    result = generate_response(prompt)
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert any(word in result.lower() for word in ["dish", "cook", "recipe", "meal", "suggest"]), \
        f"Unexpected response for '{prompt}': {result}"

class TestAdditionalIngredientScenarios:
    def test_chicken_and_rice(self):
        """Should suggest a coherent dish when both chicken and rice are given."""
        result = generate_response("I have chicken and rice.")
        assert any(word in result.lower() for word in ["chicken", "rice", "dish", "recipe"]), \
            f"Unexpected response: {result}"

    def test_chicken_lemon_parsley(self):
        """Should pick up all three fresh ingredients in a suggestion."""
        result = generate_response("I want to cook chicken with lemon and parsley.")
        for ingredient in ["chicken", "lemon", "parsley"]:
            assert ingredient in result.lower(), f"Missing '{ingredient}' in response: {result}"

    def test_empty_ingredient_list(self):
        """Should gracefully handle empty or vague input."""
        result = generate_response("I don’t know what I have.")
        assert "suggest" in result.lower() or "idea" in result.lower(), \
            f"Expected a fallback suggestion, got: {result}"

    def test_conflicting_restrictions(self):
        """Should reject recipes when restricted and allowed overlap."""
        result = generate_response("I want a recipe with chicken and pork.", ingredients=["pork"])
        assert "cannot" in result.lower() or "avoid" in result.lower(), \
            f"Expected pork restriction handling, got: {result}"

    def test_gibberish_input(self):
        """Should not crash on nonsense input."""
        result = generate_response("asdfghjkl qwertyuiop zxcvbnm")
        assert isinstance(result, str) and len(result) > 0, \
            f"Unexpected response to gibberish: {result}"
