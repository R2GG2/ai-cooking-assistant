import re

# Make sure restricted_ingredients list is defined globally somewhere:
restricted_ingredients = [
    "flour",
    "sugar",
    "turkey",
    "coconut",
    "maple syrup",
    "gelatin",
    "peanuts",
]


def generate_response(user_input, session):
    user_input_lower = user_input.lower()

    # Optional safety: ensure keys exist in session dict
    session.setdefault("restrictions", [])
    session.setdefault("equipment", [])
    session.setdefault("ingredients", [])

    # Step 1: Ask about restrictions
    if not session["restrictions"]:
        vague_indicators = [
            "i don't know",
            "not sure",
            "something healthy",
            "anything",
            "",
        ]
        no_allergy_phrases = ["no allergies", "no allergy", "none", "no restrictions"]

        # If user says no allergies or vague input, move to equipment
        if user_input_lower in no_allergy_phrases or any(
            phrase in user_input_lower for phrase in vague_indicators
        ):
            session["restrictions"] = []  # Mark restrictions as collected even if empty
            return (
                "What cooking equipment do you have available? (e.g., wok, Instant Pot, cast iron)",
                session,
            )

        detected = [item for item in restricted_ingredients if item in user_input_lower]
        if detected:
            for item in detected:
                if item not in session["restrictions"]:
                    session["restrictions"].append(item)
            restrictions_str = ", ".join(session["restrictions"])
            return (
                f"Noted! I’ll avoid {restrictions_str}. What cooking equipment do you have available?",
                session,
            )

        return (
            "Do you have any allergies or dietary restrictions I should know about?",
            session,
        )

    # Step 2: Ask about equipment
    if not session["equipment"]:
        possible_equipment = [
            "wok",
            "instant pot",
            "cast iron",
            "oven",
            "stove",
            "grill",
            "pyrex glass bakeware",
        ]

        detected_eq = []
        for eq in possible_equipment:
            pattern = r"\b" + re.escape(eq) + r"\b"
            if re.search(pattern, user_input_lower):
                detected_eq.append(eq)

        for eq in detected_eq:
            if eq not in session["equipment"]:
                session["equipment"].append(eq)

        print("DEBUG: Detected equipment:", detected_eq)  # Debug detected equipment

        if session["equipment"]:
            equipment_str = ", ".join(session["equipment"])
            return (
                f"Great, you have {equipment_str}. What ingredients do you want to use?",
                session,
            )

        return (
            "What cooking equipment do you have available? (e.g., wok, Instant Pot, cast iron)",
            session,
        )

    # Step 3: Ask about ingredients
    if not session["ingredients"]:
        if "," not in user_input_lower:
            return (
                "Please list the ingredients you want to use, separated by commas.",
                session,
            )

        ingredients = [i.strip() for i in user_input_lower.split(",") if i.strip()]
        restricted_found = [
            item for item in ingredients if item in restricted_ingredients
        ]

        if restricted_found:
            restricted_str = ", ".join(restricted_found)
            return (
                f"Some of your ingredients are restricted ({restricted_str}). Can you list other ingredients?",
                session,
            )

        session["ingredients"] = ingredients
        equipment_str = ", ".join(session["equipment"])
        return (
            f"With your {', '.join(session['ingredients'])} and your {equipment_str}, I suggest a tasty stir-fry!",
            session,
        )

    # Step 4: All info collected
    restrictions_str = ", ".join(session["restrictions"]) or "none"
    equipment_str = ", ".join(session["equipment"])
    ingredients_str = ", ".join(session["ingredients"])
    return (
        f"Ready to cook with your restrictions ({restrictions_str}), equipment ({equipment_str}), and ingredients ({ingredients_str}). Let's get started!",
        session,
    )
