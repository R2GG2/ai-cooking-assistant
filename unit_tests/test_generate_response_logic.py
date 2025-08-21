import pytest
from logic.generate_response_logic import generate_response

def test_known_ingredients():
    result = generate_response("I have chicken and potatoes.")
    assert "chicken" in result and "potatoes" in result

def test_equipment_detection():
    result = generate_response("Can I use my Instant Pot?")
    assert "instant pot" in result.lower()

def test_restricted_ingredient_response():
    result = generate_response("I want to cook with sugar and coconut", ingredients=["sugar", "coconut"])
    assert "restricted" in result.lower()

def test_unsure_user_input():
    result = generate_response("I'm not sure what I have.")
    assert "dietary restrictions" in result.lower()

def test_empty_input():
    result = generate_response("")
    assert "what you’re in the mood for" in result.lower()
