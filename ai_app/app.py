from flask import Flask, render_template, request, session, send_from_directory
from generate_response import generate_response
from pathlib import Path
from dotenv import load_dotenv
import json
import os

# Load .env variables (FLASK_APP, FLASK_ENV, PORT, etc.)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")  # TODO: set in .env for production
app.config["TEMPLATES_AUTO_RELOAD"] = True

# ---- Corrected path to static_site ----
# This will correctly resolve to: <project_root>/static_site/
TEST_PAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))

# ---- Session clearing route (for debugging/reset) ----
@app.route("/clear_session", methods=["POST"])
def clear_session():
    session.clear()
    return "Session cleared", 200

# ---- Main entry point ----
@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize session keys if missing (mutate, don't reassign)
    session.setdefault("restrictions", [])
    session.setdefault("equipment", [])
    session.setdefault("ingredients", [])

    response = ""
    user_input = ""

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        print(f"DEBUG: Received user_input: '{user_input}'")
        print(f"DEBUG: Session before generate_response: {dict(session)}")

        # Pass session to the assistant logic
        response, _ = generate_response(user_input, session)
        session.modified = True  # Ensure session mutations are saved

        print(f"DEBUG: Session after generate_response: {dict(session)}")

    return render_template("index.html", response=response)

# ---- Result history route ----
@app.route("/results")
def show_results():
    results_file = "test_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = []

    # Normalize result keys for robustness
    for r in results:
        r.setdefault("error", "")
        r.setdefault("test_name", "Unknown Test")
        r.setdefault("status", "unknown")
        r.setdefault("timestamp", "")
        r.setdefault("screenshot", "")

    return render_template("results.html", results=results)

# ---- Serve a static test page for Selenium UI testing ----
@app.route("/test_page.html")
def test_page():
    return send_from_directory(TEST_PAGES_DIR, "test_page.html")

# ---- Run the app ----
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=True)
