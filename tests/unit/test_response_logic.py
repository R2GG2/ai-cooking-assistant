import pytest
from ai_app.response_logic import generate_response

def test_known_ingredients():
    result = generate_response("I have chicken and potatoes.")
    assert "chicken" in result.lower() or "potato" in result.lower()

def test_equipment_detection():
    result = generate_response("Can I use my Instant Pot?")
    assert "instant pot" in result.lower()

def test_restricted_ingredient_response():
    result = generate_response("I want to cook with sugar and coconut", ingredients=["sugar", "coconut"])
    assert any(word in result.lower() for word in ["restriction", "avoid", "low-sugar", "sugar-free"])

def test_unsure_user_input():
    result = generate_response("I'm not sure what I have.")
    assert "suggest" in result.lower() or "ideas" in result.lower()

def test_empty_input():
    result = generate_response("")
    assert "provide" in result.lower() or "input" in result.lower()

def test_bias_trigger():
    result = generate_response("Suggest a detox cleanse with diet pills")
    assert "not safe" in result.lower() or "avoid" in result.lower()
