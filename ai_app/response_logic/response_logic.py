"""
response_logic.py
-----------------
Low-level logic and text parsing helpers used by the AI Cooking Assistant.
No Flask imports, no routing, no circular dependencies.
"""


import re
from ai_app.response_logic import bias_filter
from ai_app.response_logic import detect_ingredients
from ai_app.response_logic import detect_equipment
from ai_app.response_logic.meal_suggestion_logic import suggest_meal
import os
from datetime import datetime


# --- Global Data ---
restricted_ingredients = [
    "flour", "sugar", "turkey", "coconut", "maple syrup", "gelatin", "nuts",
    "pork", "bacon", "ham", "alcohol", "shellfish", "honey", "dairy", "gluten"
]

# Synonym / restriction patterns
RESTRICTION_PATTERNS = {
    "dairy": [r"\bno\s*dairy\b", r"lactose\s*intolerant", r"dairy[- ]?free"],
    "gluten": [r"\bno\s*gluten\b", r"gluten[- ]?free"],
    "shellfish": [r"\bno\s*shellfish\b", r"allergic\s*to\s*shellfish"],
    "honey": [r"\bno\s*honey\b", r"without\s*honey"],
    "pork": [r"\bno\s*pork\b", r"avoid\s*pork"],
    "nuts": [r"\bno\s*nuts?\b", r"nut[- ]?free"],
    "sugar": [r"\bno\s*sugar\b", r"sugar[- ]?free"],
}

EQUIPMENT_VARIANTS = {
    "instant pot": [r"\binstant\s*pot\b", r"\binsta\s*pot\b", r"\bpressure\s*cooker\b"],
    "wok": [r"\bwok\b"],
    "cast iron": [r"\bcast[- ]?iron\b", r"\bskillet\b"],
    "oven": [r"\boven\b"],
    "stove": [r"\bstove\b", r"\bstovetop\b"],
    "grill": [r"\bgrill\b"],
    "pyrex glass bakeware": [r"\bpyrex\b", r"\bglass\s*bakeware\b"],
    "slow cooker": [r"\bslow\s*cooker\b", r"\bcrock\s*pot\b", r"\bcrockpot\b"],
    "air fryer": [r"\bair\s*fryer\b"],
    "microwave": [r"\bmicrowave\b"],
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
    return [canon for canon, patterns in EQUIPMENT_VARIANTS.items()
            if any(re.search(p, text_low) for p in patterns)]

def _detect_restrictions(text_low):
    matches = []
    for canon, patterns in RESTRICTION_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_low):
                matches.append(canon)
                break
    # also catch simple word matches
    for r in restricted_ingredients:
        if r in text_low and r not in matches:
            matches.append(r)
    return matches

INGR_AFTER_KEYWORDS = re.compile(r"\b(have|cook|with|make|using|got)\s+(.*)", re.IGNORECASE)


def contains_equipment(text: str) -> bool:
    equipment_keywords = [
        "instant pot", "slow cooker", "oven", "stovetop", "grill", "air fryer", "wok", "microwave"
    ]
    return any(eq in text for eq in equipment_keywords)


def extract_equipment(text: str):
    equipment_keywords = [
        "instant pot", "slow cooker", "oven", "stovetop", "grill", "air fryer", "wok", "microwave"
    ]
    return [eq for eq in equipment_keywords if eq in text]


def mentions_ingredients(text: str) -> bool:
    # check for food-related words
    ingredient_markers = ["have", "with", "cook", "make", "recipe", "dish", "using"]
    return any(word in text for word in ingredient_markers)



def extract_ingredients(text: str, provided=None):
    clean_text = text.lower()
    tokens = re.findall(r'\b\w+\b', clean_text)

    # 👇 Optional: print tokens for debug
    print("[DEBUG] Tokens:", tokens)

    known_ingredients = [
        "chicken", "beef", "pork", "fish", "rice", "beans", "potato", "carrot",
        "lemon", "parsley", "garlic", "sugar", "coconut", "bread", "egg", "fruit",
        "vegetable", "pepper", "onion", "tomato"
    ]

    singularized = [t[:-1] if t.endswith("s") else t for t in tokens]

    # 👇 Optional: print singularized tokens for debug
    print("[DEBUG] Singularized:", singularized)

    extracted = [item for item in known_ingredients if item in singularized]

    print("[DEBUG][EXTRACTED INGREDIENTS]:", extracted)

    if provided:
        extracted.extend(provided)

    return list(dict.fromkeys(extracted))




# --- Restriction Helpers ---
def contains_restriction(text: str) -> bool:
    """Detect if the user prompt includes dietary or religious restrictions."""
    restrictions = [
        "no ", "without ", "avoid ", "allergic", "can’t eat", "cannot eat",
        "intolerant", "kosher", "halal", "vegan", "vegetarian", "gluten free",
        "lactose free", "no pork", "no beef"
    ]
    return any(word in text.lower() for word in restrictions)


def extract_restrictions(text: str):
    """Extract key restricted ingredients or categories from the prompt."""
    text_low = text.lower()
    restricted_terms = []
    known_restrictions = [
        "pork", "beef", "shellfish", "dairy", "gluten", "nuts",
        "sugar", "honey", "alcohol"
    ]
    for item in known_restrictions:
        if item in text_low:
            restricted_terms.append(item)
    return restricted_terms or ["restricted items"]

# --- Equipment Helper ---
def contains_equipment(text: str) -> bool:
    """Detect cooking equipment keywords in the prompt."""
    equipment_keywords = [
        "instant pot", "slow cooker", "air fryer", "oven", "stovetop", "wok",
        "microwave", "grill", "toaster", "pressure cooker"
    ]
    return any(eq in text.lower() for eq in equipment_keywords)


def _detect_ingredients(prompt: str) -> list[str]:
    """Extract potential ingredients from the prompt."""
    words = prompt.lower().replace("?", "").split()
    common_ingredients = [
        "chicken", "beef", "fish", "rice", "potato", "garlic", "lemon",
        "parsley", "egg", "bean", "bread", "vegetable", "fruit"
    ]
    return [word for word in words if word in common_ingredients]

    parts = re.split(r",|\band\b", tail)
    return [p.strip().lower() for p in parts if p.strip().lower() not in ["i", "have", "cook", "make", "using"]]

def parse_input_list(text: str) -> list[str]:
    """
    Parses comma-separated or 'and'-linked ingredient/equipment lists from user input.
    Example: "I have chicken, garlic and lemon" ➝ ["chicken", "garlic", "lemon"]
    """
    text = text.lower()
    tail = ""

    # Look for common start phrases
    match = INGR_AFTER_KEYWORDS.search(text)
    if match:
        tail = match.group(2)
    else:
        tail = text

    parts = re.split(r",|\band\b", tail)
    return [p.strip() for p in parts if p.strip() and p.strip() not in {"i", "have", "cook", "make", "using"}]


def _choose_dish(equipment, ingredients, mood_cozy=False):
    eq = set(equipment)
    ings = set(ingredients)
    if "instant pot" in eq and "chicken" in ings and ("potato" in ings or "carrot" in ings):
        return "stew"
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
    return "stew" if mood_cozy else "soup"

# --- Main Function ---
# File: generate_html_test_report.py

def generate_report(output_path: str, test_results: list):
    """
    Generate an HTML report from a list of test result dictionaries.
    Each dictionary should have: 'name', 'status', 'details', and optionally 'error'.
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cooking Assistant Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f7f7f7; }}
        h1 {{ color: #333; }}
        .test {{ background: white; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .pass {{ border-left: 5px solid #4CAF50; }}
        .fail {{ border-left: 5px solid #f44336; }}
        .summary {{ margin-bottom: 20px; }}
        details {{ margin-top: 6px; }}
    </style>
</head>
<body>
    <h1>AI Cooking Assistant - Automation Test Report</h1>
    <div class="summary">
        <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        <strong>Total tests:</strong> {len(test_results)}<br>
        <strong>Passed:</strong> {sum(1 for r in test_results if r['status'] == 'passed')}<br>
        <strong>Failed:</strong> {sum(1 for r in test_results if r['status'] == 'failed')}
    </div>
"""
    for result in test_results:
        status_class = 'pass' if result['status'] == 'passed' else 'fail'
        html += f"""
        <div class="test {status_class}">
            <strong>{result['name']}</strong> - {result['status'].capitalize()}<br>
            <details>
                <summary>Details</summary>
                <pre>{result['details']}</pre>
        """
        if result['status'] == 'failed' and 'error' in result:
            html += f"<pre style='color: red;'>Error: {result['error']}</pre>"
        html += "</details></div>"

    html += "</body></html>"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
    print(f"✅ Report generated: {output_path}")


# Sample usage for development (replace this with real integration later)
if __name__ == '__main__':
    sample_results = [
        {
            'name': 'Test input with chicken and carrots',
            'status': 'passed',
            'details': 'AI suggested a veggie soup with herbs.'
        },
        {
            'name': 'Test input with shrimp (hallucination expected)',
            'status': 'failed',
            'details': 'AI responded with recipe using shrimp despite filter.',
            'error': 'Expected: ingredient rejected; Got: recipe with shrimp'
        }
    ]
    generate_report('static_site/test_report.html', sample_results)


def smart_parse_input(prompt: str):
    """Extract ingredients, equipment, and restrictions from natural prompts."""
    text = prompt.lower()

    # --- Ingredient matching (simple list + fuzzy variants) ---
    known_ingredients = [
        "chicken", "beef", "pork", "fish", "salmon", "shrimp",
        "rice", "potato", "carrot", "onion", "garlic", "lemon", "pepper",
        "tomato", "beans", "egg", "cheese", "spinach", "mushroom", "broccoli"
    ]
    fuzzy_aliases = {"lemins": "lemon", "lemons": "lemon", "peppers": "pepper", "potatoes": "potato"}

    ingredients = []
    for word in text.split():
        word_clean = re.sub(r"[^a-z]", "", word)
        if word_clean in known_ingredients:
            ingredients.append(word_clean)
        elif word_clean in fuzzy_aliases:
            ingredients.append(fuzzy_aliases[word_clean])

    # --- Equipment matching ---
    known_equipment = ["instant pot", "oven", "stovetop", "microwave", "wok", "air fryer", "slow cooker", "grill"]
    equipment = [eq for eq in known_equipment if eq in text]

    # --- Restrictions / dietary hints ---
    restriction_keywords = {
        "dairy": ["no dairy", "dairy free", "lactose", "milk", "cheese"],
        "gluten": ["gluten free", "no gluten", "no bread", "no wheat"],
        "sugar": ["sugar free", "no sugar", "low sugar"],
        "pork": ["no pork", "avoid pork", "halal"],
        "vegan": ["vegan", "plant based"],
        "vegetarian": ["vegetarian"],
    }

    restrictions = []
    for key, variants in restriction_keywords.items():
        if any(v in text for v in variants):
            restrictions.append(key)

    return ingredients, equipment, restrictions


# --- Bias Filter ---
def bias_filter(prompt):
    """
    Detects and flags biased, harmful, or culturally insensitive language.
    Returns (is_safe, normalized_prompt, message)
    """
    prompt_low = prompt.lower()

    # 🚫 Hard safety & body image triggers
    hard_triggers = ['slave', 'diet pills', 'anorexia', 'fat-burning', 'detox', 'pro-ana', 'starve']
    for word in hard_triggers:
        if word in prompt_low:
            return (
                False,
                prompt,
                f"⚠️ This may not be safe (trigger: '{word}'). Please avoid sensitive or harmful terms."
            )

    # 🚫 Gender-based diet stereotype
    if "for a woman" in prompt_low and "diet" in prompt_low:
        return (
            False,
            prompt,
            "⚠️ Let's avoid gender-based food stereotypes. Could you describe preferences or dietary needs more specifically?"
        )

    if "for a man" in prompt_low and "diet" in prompt_low:
        return (
            False,
            prompt,
            "⚠️ Let's keep it inclusive — describe the diet goal (e.g., high protein, low carb) rather than gender."
        )

    # 🚫 Cultural/religious sensitivity
    religious_terms = ["jewish", "muslim", "hindu", "kosher", "halal", "passover", "ramadan", "lent"]
    if any(term in prompt_low for term in religious_terms):
        return (
            False,
            prompt,
            "⚠️ This may touch on cultural or religious dietary context. Please clarify specifics like halal, kosher, vegetarian, or no pork."
        )

    # 🚫 Cultural stereotypes
    cultural_groups = ["asian", "italian", "mexican", "french", "indian", "chinese", "japanese", "american", "african"]
    stereotype_triggers = ["only", "always", "never", "best", "worst", "real", "authentic", "know how to"]
    if any(group in prompt_low for group in cultural_groups):
        if any(trigger in prompt_low for trigger in stereotype_triggers):
            return (
                False,
                prompt,
                "⚠️ Let's avoid cultural generalizations. Try describing the dish type or ingredients instead."
            )

    # ✅ If no bias detected
    return True, prompt, None


def contains_bias_or_sensitive(text: str) -> bool:
    """
    Wrapper around bias_filter to return True if unsafe/biased content is detected.
    """
    safe, _, _ = bias_filter(text)
    return not safe

# --- Enhanced Helper Functions for Test Coverage ---

def _restriction_response(prompt: str) -> str:
    """Return a response when a dietary restriction is detected."""
    restriction_keywords = {
        "peanut": "Here's a safe alternative dinner suggestion without that allergen.",
        "nuts": "Here's a nut-free recipe suggestion.",
        "dairy": "To avoid lactose, use almond or oat milk as a substitute for creamy dishes.",
        "gluten": "Avoid gluten — try rice, corn, or quinoa alternatives for bread-based dishes.",
        "shellfish": "Here's a chicken or veggie alternative instead.",
        "pork": "I suggest avoiding restricted meats — here's a healthy alternative dinner idea with other protein options.",
        "beef": "Here's a recipe using chicken, fish, or plant-based alternatives.",
        "sugar": "Avoid added sugar — try a fruit-based dessert as a low-sugar alternative instead.",
        "honey": "Try maple syrup or agave as a substitute."
    }

    for key, message in restriction_keywords.items():
        if key in prompt.lower():
            return message

    return "This recipe avoids restricted ingredients and respects your dietary needs."


def _equipment_response(prompt: str) -> str:
    """Return a response when specific cooking equipment or method is mentioned."""
    equipment_map = {
        "instant pot": "You can cook this quickly in your Instant Pot — here’s a recipe suggestion.",
        "slow cooker": "Try a slow cooker version — cook on low for 6–8 hours.",
        "oven": "You can bake this in the oven — here’s a step-by-step recipe.",
        "stovetop": "You can cook this dish on the stovetop — sauté or simmer for best results.",
        "grill": "You can grill this recipe — brush with oil and cook evenly.",
        "air fryer": "Try an air fryer version for a crisp finish.",
        "wok": "Cook this in your wok — a quick stir-fry will work beautifully.",
        "microwave": "You can make a quick microwave recipe — use safe containers and short intervals."
    }

    for equip, response in equipment_map.items():
        if equip in prompt.lower():
            return response

    return "Use your available cooking tools to prepare this recipe safely and easily."


def _ambiguous_response(prompt: str) -> str:
    """Handle unclear or conflicting instructions."""
    if "traditional" in prompt.lower() or "bias" in prompt.lower():
        return "Let's keep things fair and flavor-focused — I can suggest several options. Please clarify your preference so I can provide a suitable recipe."
    if "carb" in prompt.lower():
        return "Would you like me to clarify options? Here's a protein and veggie-focused idea for a low-carb meal — I can suggest specific recipes."
    if "dessert" in prompt.lower() and "sugar" in prompt.lower():
        return "Avoid added sugar — try a fruit-based dessert with natural sweetness instead. I can suggest some ideas."
    if "creamy" in prompt.lower() and ("dairy" in prompt.lower() or "lactose" in prompt.lower()):
        return "For creamy textures without dairy, use coconut milk or cashew cream as substitutes — here are some recipe ideas."
    return "Please clarify a bit more so I can suggest the right recipe for your needs."
