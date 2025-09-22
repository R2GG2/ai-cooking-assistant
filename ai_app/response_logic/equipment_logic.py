# Equipment detection logic

EQUIPMENT_KEYWORDS = ["instant pot", "wok", "cast iron", "air fryer", "oven"]

def detect_equipment(text_low: str):
    """Return a list of matched equipment terms (lowercase)."""
    return [item for item in EQUIPMENT_KEYWORDS if item in text_low]
