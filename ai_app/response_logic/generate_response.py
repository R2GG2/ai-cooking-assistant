import re
from ai_app.response_logic.bias_detection import bias_filter

# --- Global Data ---
restricted_ingredients = [
    "flour", "sugar", "turkey", "coconut", "maple syrup", "gelatin", "nuts",
    "pork", "bacon", "ham", "alcohol"
]

EQUIPMENT_VARIANTS = {
    "instant pot": [r"\binstant\s*pot\b", r"\binsta\s*pot\b", r"\bpressure\s*cooker\b"],
    "wok": [r"\bwok\b"],
    "cast iron": [r"\bcast[- ]?iron\b", r"\bskillet\b"],
    "oven": [r"\boven\b"],
    "stove": [r"\bstove\b", r"\bstovetop\b"],
    "grill": [r"\bgrill\b"],
    "pyrex glass bakeware": [r"\bpyrex\b", r"\bglass\s*bakeware\b"],
    "slow cooker": [r"\bslow\s*cooker\b", r"\bcrock\s*pot\b", r"\bcrockpot\b"],
}

# --- Helpers ---
def _dedupe(seq):
    seen = set()
    out = []
    for x in seq:
        xl = x.strip().lower()
        if xl and xl not in seen:
            out.append(xl)
            seen.add(xl)
    return out

def _detect_equipment(text_low):
    return [canon for canon, patterns in EQUIPMENT_VARIANTS.items() if any(re.search(p, text_low) for p in patterns)]

def _detect_restrictions(text_low):
    if any(p in text_low for p in ["no allergies", "no allergy", "none", "no restrictions"]):
        return []
    return [r for r in restricted_ingredients if r in text_low]

INGR_AFTER_HAVE = re.compile(r"\b(i\s*have|using|got)\s+(.*)", re.IGNORECASE)

def _detect_ingredients(text_low):
    tail = None
    m = INGR_AFTER_HAVE.search(text_low)
    if m:
        tail = m.group(2)
    elif "," in text_low:
        tail = text_low

    if not tail:
        return []

    parts = re.split(r",|\band\b", tail)
    return [p.strip().lower() for p in parts if p.strip().lower() not in ["i", "have"]]

def _choose_dish(equipment, ingredients, mood_cozy=False):
    eq = set(equipment)
    ings = set(ingredients)
    if "instant pot" in eq and "chicken" in ings and ("potato" in ings or "carrot" in ings):
        return "stew"
    if "wok" in eq:
        return "stir-fry"
    return "stew" if mood_cozy else "soup"

# --- Main Function ---
def generate_response(user_input, ingredients=None, equipment=None, restrictions=None):
    user_input = user_input.lower()

    is_safe, prompt, warning = bias_filter(user_input)
    if not is_safe:
        return warning

    # ❌ Empty input
    if not user_input.strip():
        return "Tell me more about what you’re in the mood for and what tools or ingredients you have."

    # ❓ Unsure user
    if "i don't know" in user_input or "not sure" in user_input:
        return "Can you tell me if you have any dietary restrictions or what ingredients you have at home?"

  # 🔹 Auto-detect ingredients if none provided
    if not ingredients:
        common_ingredients = ["chicken", "potatoes", "onions", "carrots", "beef", "rice", "lentils", "eggs", "broccoli"]
        ingredients = [item for item in common_ingredients if item in user_input]

    # 🍴 Ingredients handling
    if ingredients:
        ingredients = [i.strip().lower() for i in ingredients]
        restricted_used = [item for item in ingredients if item in restricted_ingredients]
        if restricted_used:
            return "Some of your ingredients are restricted. Can you list others?"
        return f"With what you have, I suggest a cozy meal using your {', '.join(ingredients)}."


   # 🔹 Equipment-based suggestions
    if not equipment:
        equipment_keywords = ["instant pot", "wok", "cast iron", "air fryer", "oven"]
        equipment = [item for item in equipment_keywords if item in user_input]
 
    if equipment:
        return (
            f"With what you have, I suggest a cozy meal to get started! "
            f"Your {', '.join(equipment)} will work great. What ingredients are you working with?"
        )


    # ✅ Final fallback
    return "Tell me more about what you’re in the mood for and what tools or ingredients you have."


# --- Bias Filter ---
def bias_filter(prompt):
    prompt_low = prompt.lower()

    # 🚫 Hard triggers
    hard_triggers = ['slave', 'diet pills', 'anorexia', 'fat-burning', 'detox']
    for word in hard_triggers:
        if word in prompt_low:
            return False, prompt, (
                f"⚠️ Your prompt includes potentially inappropriate or sensitive content ('{word}'). "
                "Could you rephrase or clarify what you mean?"
            )

    # 🚫 Gender-based diet stereotype
    if "for a woman" in prompt_low and "diet" in prompt_low:
        return False, prompt, (
            "⚠️ Let's avoid gender-based food stereotypes. "
            "Could you describe preferences or dietary needs more specifically?"
        )

    # 🚫 Cultural/religious sensitivity (generic)
    if any(term in prompt_low for term in ["jewish", "muslim", "hindu", "kosher", "halal", "passover", "ramadan"]):
        return False, prompt, (
            "⚠️ This may touch on cultural or religious dietary context. "
            "Please clarify specifics like 'halal', 'kosher', or vegetarian preferences."
        )


    # 🚫 Cultural stereotypes
    if any(group in prompt_low for group in ["asian", "italian", "mexican", "french", "indian", "chinese", "japanese"]):
        if any(trigger in prompt_low for trigger in ["only", "always", "never", "best", "know how to"]):
            return False, prompt, (
                "⚠️ Let's avoid cultural stereotypes. Could you focus on the dish or ingredients instead?"
            )
        
    # 🚫 Cultural/religious sensitivity (generic)
    if any(term in prompt_low for term in ["jewish", "muslim", "hindu", "kosher", "halal", "passover", "ramadan"]):
        return False, prompt, (
            "⚠️ This may touch on cultural or religious dietary context. "
            "Please clarify specifics like 'halal', 'kosher', 'vegetarian', or 'no pork'."
        )

    # ✅ Safe prompt
    return True, prompt, None

