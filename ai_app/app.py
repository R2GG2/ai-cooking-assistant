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

# ---- Utility paths ----
# Repo root = parent of this file's folder (ai_app/)
REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_PAGES_DIR = REPO_ROOT / "test_pages"


@app.route("/clear_session", methods=["POST"])
def clear_session():
    session.clear()
    return "Session cleared", 200


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

        # Pass the session so generate_response can mutate it; do not reassign session
        response, _ = generate_response(user_input, session)
        session.modified = True  # ensure Flask persists the mutation

        print(f"DEBUG: Session after generate_response: {dict(session)}")

    return render_template("index.html", response=response)


@app.route("/results")
def show_results():
    results_file = "test_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = []

    # Normalize keys for template robustness
    for r in results:
        r.setdefault("error", "")
        r.setdefault("test_name", "Unknown Test")
        r.setdefault("status", "unknown")
        r.setdefault("timestamp", "")
        r.setdefault("screenshot", "")

    return render_template("results.html", results=results)


# ---- Serve static test page for Selenium ----
@app.route("/test_page.html")
def test_page():
    # Serve test_pages/test_page.html at http://127.0.0.1:<PORT>/test_page.html
    return send_from_directory(TEST_PAGES_DIR, "test_page.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # Bind to localhost for local testing; set FLASK_RUN_HOST in .env if needed
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=True)
