import re

def bias_filter(prompt: str):
    bias_patterns = {
        "gender": r"\b(woman|man|girl|boy)\b",
        "cultural": r"\b(Muslim|Italian|Jewish|Hindu|Christian|Chinese|Mexican|Black|White)\b",
        "stereotype": r"only .* know how to|real men|real women|as a [a-z]+ woman",
    }

    for category, pattern in bias_patterns.items():
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, category, f"⚠️ This may contain {category}-biased content."

    return True, None, None
