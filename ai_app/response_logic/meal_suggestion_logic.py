import re
from ai_app.response_logic import bias_filter
from ai_app.response_logic import detect_ingredients
from ai_app.response_logic import detect_equipment

def choose_dish(equipment, ingredients, mood_cozy=False):
    eq = set((equipment or []))
    ings = set((ingredients or []))

    if mood_cozy:
        if "instant pot" in eq and "chicken" in ings and ("potato" in ings or "carrot" in ings):
            return "Instant Pot chicken stew"
        if "oven" in eq and "potato" in ings:
            return "Oven-roasted potato bake"
        if "oven" in eq and "chicken" in ings and "carrot" in ings:
            return "Roast chicken and vegetables"
        if "cast iron" in eq and "beef" in ings:
            return "Cast iron-seared beef"
        if "stovetop" in eq and "broth" in ings:
            return "Stovetop comforting broth soup"
        if "wok" in eq and "rice" in ings:
            return "Wok-fried cozy rice bowl"
        if "slow cooker" in eq and "carrot" in ings:
            return "Slow-cooked veggie stew"
        if "microwave" in eq and "vegetables" in ings:
            return "Microwaveable cozy mug soup"
        return "Cozy veggie soup"

    # Neutral (non-cozy) logic
    if "instant pot" in eq and "chicken" in ings and ("potato" in ings or "carrot" in ings):
        return "Instant Pot chicken stew"
    if "wok" in eq:
        return "stir-fry"
    if "oven" in eq:
        return "bake" if "vegetables" in ings else "roast"
    if "grill" in eq:
        return "grilled dish"
    if "air fryer" in eq:
        return "air fried meal"
    if "microwave" in eq:
        return "microwave snack"

    return "soup"


def suggest_meal(equipment, ingredients, restrictions=None, mood_cozy=False):
    restriction_note = ""
    safe_ingredients = ingredients or []

    if restrictions:
        restriction_note = f" (avoiding: {', '.join(restrictions)})"
        safe_ingredients = [i for i in ingredients or [] if i not in restrictions]

    dish = choose_dish(equipment, safe_ingredients, mood_cozy)

    return (
        f"Suggested dish: {dish.capitalize()}.{restriction_note} "
        "Base: aromatics + broth; add your ingredients; finish with herbs/acid. Serves 2–4."
    )
