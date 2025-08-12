restricted_ingredients = [
    "flour",
    "sugar",
    "turkey",
    "coconut",
    "maple syrup",
    "gelatin",
]


def generate_response(user_input, ingredients=None, equipment=None, restrictions=None):
    user_input = user_input.lower()

    # Guess from raw input if no structured args passed
    if not ingredients:
        guessed_ingredients = []
        for word in ["chicken", "potatoes", "onions", "carrots"]:
            if word in user_input:
                guessed_ingredients.append(word)
        ingredients = guessed_ingredients

    if not equipment:
        if "instant pot" in user_input:
            equipment = ["instant pot"]

    if any(phrase in user_input for phrase in ["i don't know", "not sure"]):
        return "Can you tell me if you have any dietary restrictions or what ingredients you have at home?"

    if restrictions:
        for item in restricted_ingredients:
            if item in restrictions:
                return f"Noted! I’ll avoid {item}. Do you have any preferred proteins like chicken, beef, or fish?"

    if ingredients:
        if any(item in restricted_ingredients for item in ingredients):
            return "Some of your ingredients are restricted. Can you list others?"

        return f"With what you have, I suggest a cozy Instant Pot stew using your {', '.join(ingredients)}."

    return "Tell me more about what you’re in the mood for and what tools you have (e.g., wok, cast iron, Instant Pot)."
