# Ingredient detection logic

COMMON_INGREDIENTS = [
    "chicken", "potatoes", "onions", "carrots", "beef",
    "rice", "lentils", "eggs", "broccoli", "pork",
    "fish", "salmon", "lemon", "parsley", "garlic",
    "beans", "bread", "pasta", "cheese", "spinach",
    "mushrooms", "soy sauce", "turkey", "cranberries",
    "dill", "tomato sauce"
]

def detect_ingredients(text_low: str):
    """Return a list of matched known ingredients (lowercase)."""
    return [item for item in COMMON_INGREDIENTS if item in text_low]
