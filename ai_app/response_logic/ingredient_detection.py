# Ingredient detection logic

COMMON_INGREDIENTS = [
    "chicken", "potatoes", "onions", "carrots", "beef",
    "rice", "lentils", "eggs", "broccoli"
]

def detect_ingredients(text_low: str):
    """Return a list of matched known ingredients (lowercase)."""
    return [item for item in COMMON_INGREDIENTS if item in text_low]
