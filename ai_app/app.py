# ai_app/app.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # ✅ Add project root to Python path

from typing import List
from flask import Flask, render_template, request, session, send_from_directory, jsonify
from dotenv import load_dotenv
import json
import base64

from ai_app.response_logic.response_logic import generate_response

print("🧠 Running:", __file__)


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")
app.config["TEMPLATES_AUTO_RELOAD"] = True

# ✅ Updated path to point to correct test_page.html directory
TEST_PAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "static_site"))
print(f"TEST_PAGES_DIR is set to: {TEST_PAGES_DIR}")



# ---------- Helpers ----------
def _csv(items: List[str]) -> str:
    return ", ".join(items) if items else "none"

def _suggest_dish_from_state(equip: List[str], restrict: List[str], ingred: List[str]) -> str:
    equip_l = [e.lower() for e in equip]
    ingred_l = [i.lower() for i in ingred]
    restrict_l = [r.lower() for r in restrict]

    if any("instant pot" in e for e in equip_l):
        method = "Instant Pot"
    elif any(k in equip_l for k in ["slow cooker", "crockpot", "crock pot"]):
        method = "Slow Cooker"
    else:
        method = "Stovetop"

    protein = next((p for p in ["chicken", "beef", "pork", "lamb", "salmon", "turkey"] if any(p in i for i in ingred_l)), None)
    dish = "stew" if (protein and any(v in ingred_l for v in ["potato", "potatoes"]) and any(v in ingred_l for v in ["carrot", "carrots"])) else "soup"

    restrictions_note = " (keeps your restrictions in mind)" if (
        "flour" in restrict_l or "sugar" in restrict_l or any("avoid" in r for r in restrict_l)
    ) else ""

    name_bits = [method] + ([protein.capitalize()] if protein else []) + ["and Veggie", dish.capitalize()]
    recipe_name = " ".join(name_bits)

    blurb = f"{recipe_name}{restrictions_note}. Base: aromatics + broth; add {', '.join(sorted(set(ingred_l)) or ['your ingredients'])}; finish with herbs/acid. Serves 2–4."
    return blurb

def _compose_contextual_response(basic_response: str) -> str:
    equipment = session.get("equipment", [])
    restrictions = session.get("restrictions", [])
    ingredients = session.get("ingredients", [])

    summary = (
        "Plan so far:\n"
        f"- Equipment: {_csv(equipment)}\n"
        f"- Restrictions: {_csv(restrictions)}\n"
        f"- Ingredients: {_csv(ingredients)}\n"
    )
    suggestion = _suggest_dish_from_state(equipment, restrictions, ingredients)
    return f"{basic_response}\n\n{summary}\nSuggested dish: {suggestion}"

# ---- Routes ----
@app.route("/clear_session", methods=["POST"])
def clear_session():
    session.clear()
    return "Session cleared", 200

@app.route("/", methods=["GET", "POST"])
def index():
    session.setdefault("restrictions", [])
    session.setdefault("equipment", [])
    session.setdefault("ingredients", [])
    session.setdefault("messages", [])

    response = ""
    if request.method == "POST":
        user_input = (request.form.get("user_input", "") or "").strip()
        session["messages"].append({"role": "user", "content": user_input})
        basic_response, _ = generate_response(user_input, session)
        session.modified = True
        response = _compose_contextual_response(basic_response)
        session["messages"].append({"role": "assistant", "content": response})
    return render_template("index.html", response=response)

@app.route("/results")
def show_results():
    results_file = "test_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = []
    for r in results:
        r.setdefault("error", "")
        r.setdefault("test_name", "Unknown Test")
        r.setdefault("status", "unknown")
        r.setdefault("timestamp", "")
        r.setdefault("screenshot", "")
    return render_template("results.html", results=results)

@app.route("/test_page.html")
def test_page():
    return render_template("test_page.html")


@app.route("/health")
def health():
    return "ok", 200

@app.route("/api/message", methods=["POST"])
def api_message():
    session.setdefault("restrictions", [])
    session.setdefault("equipment", [])
    session.setdefault("ingredients", [])
    session.setdefault("messages", [])

    data = request.get_json(force=True) or {}
    user_input = (data.get("text") or "").strip()
    if user_input:
        session["messages"].append({"role": "user", "content": user_input})

    basic_response, _ = generate_response(user_input, session)
    session.modified = True
    reply = _compose_contextual_response(basic_response)
    session["messages"].append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

# ---- Run ----
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    pytest_mode = os.getenv("PYTEST_RUN") == "1"
    app.run(
        host="127.0.0.1",
        port=port,
        debug=not pytest_mode,
        use_reloader=not pytest_mode,
    )
