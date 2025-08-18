restricted_ingredients = [
    "flour",
    "sugar",
    "turkey",
    "coconut",
    "maple syrup",
    "gelatin",
    "nuts",
]

def generate_response(user_input, ingredients=None, equipment=None, restrictions=None):
    user_input = user_input.lower()

    # 🔍 Ingredient guessing from raw input
    common_ingredients = ["chicken", "potatoes", "onions", "carrots", "beef", "rice", "lentils", "eggs", "broccoli"]
    if not ingredients:
        ingredients = [item for item in common_ingredients if item in user_input]

    # 🔧 Equipment guessing from raw input
    if not equipment:
        equipment_keywords = ["instant pot", "wok", "cast iron", "air fryer", "oven"]
        equipment = [item for item in equipment_keywords if item in user_input]

    # 🤔 Handle vague input
    if any(phrase in user_input for phrase in ["i don't know", "not sure"]):
        return "Can you tell me if you have any dietary restrictions or what ingredients you have at home?"

    # 🚫 Filter based on restrictions
    if restrictions:
        for item in restricted_ingredients:
            if item in restrictions:
                return f"Noted! I’ll avoid {item}. Do you have any preferred proteins like chicken, beef, or fish?"

    # 🧼 Ingredient restriction check
    if ingredients:
        restricted_used = [item for item in ingredients if item in restricted_ingredients]
        if restricted_used:
            return "Some of your ingredients are restricted. Can you list others?"

    # ✅ Valid response generation
    if ingredients:
        return f"With what you have, I suggest a cozy meal using your {', '.join(ingredients)}."

    # 🔁 Fallback if nothing is known
    return "Tell me more about what you’re in the mood for and what tools you have (e.g., wok, cast iron, Instant Pot)."
