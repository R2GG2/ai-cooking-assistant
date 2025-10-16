import pytest
from ai_app.response_logic.meal_suggestion_logic import suggest_meal

def test_suggest_meal_cozy_stew():
    result = suggest_meal(
        equipment=["instant pot"],
        ingredients=["chicken", "potato"],
        restrictions=["dairy"],
        mood_cozy=True
    )
    # Use lowercase comparison on both sides
    assert "instant pot chicken stew" in result.lower()
    assert "avoiding: dairy" in result.lower()


def test_cozy_oven_roasted_potato_bake():
    result = suggest_meal(
        equipment=["oven"],
        ingredients=["potato"],
        mood_cozy=True
    )
    assert "Oven-roasted potato bake" in result


def test_cozy_roast_chicken_and_vegetables():
    result = suggest_meal(
        equipment=["oven"],
        ingredients=["chicken", "carrot"],
        mood_cozy=True
    )
    assert "Roast chicken and vegetables" in result


def test_cozy_cast_iron_beef():
    result = suggest_meal(
        equipment=["cast iron"],
        ingredients=["beef"],
        mood_cozy=True
    )
    assert "Cast iron-seared beef" in result


def test_cozy_stovetop_broth_soup():
    result = suggest_meal(
        equipment=["stovetop"],
        ingredients=["broth", "garlic"],
        mood_cozy=True
    )
    assert "Stovetop comforting broth soup" in result


def test_cozy_wok_rice_bowl():
    result = suggest_meal(
        equipment=["wok"],
        ingredients=["rice", "vegetables"],
        mood_cozy=True
    )
    assert "Wok-fried cozy rice bowl" in result


def test_cozy_slow_cooker():
    result = suggest_meal(
        equipment=["slow cooker"],
        ingredients=["carrot"],
        mood_cozy=True
    )
    assert "Slow-cooked veggie stew" in result


def test_cozy_microwave():
    result = suggest_meal(
        equipment=["microwave"],
        ingredients=["vegetables"],
        mood_cozy=True
    )
    assert "Microwaveable cozy mug soup" in result


def test_cozy_no_equipment():
    result = suggest_meal(
        equipment=[],
        ingredients=["carrot"],
        mood_cozy=True
    )
    assert "Cozy veggie soup" in result
