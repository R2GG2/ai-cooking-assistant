from flask import Flask, render_template, request, session
from generate_response import generate_response
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key!
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/clear_session", methods=["POST"])
def clear_session():
    session.clear()
    return "Session cleared", 200


@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize session keys if missing
    session.setdefault("restrictions", [])
    session.setdefault("equipment", [])
    session.setdefault("ingredients", [])

    response = ""
    user_input = ""

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        print(f"DEBUG: Received user_input: '{user_input}'")
        print(f"DEBUG: Session before generate_response: {dict(session)}")

        response, _ = generate_response(
            user_input, session
        )  # Pass session, do not reassign
        session.modified = True  # Mark session as modified to save changes

        print(f"DEBUG: Session after generate_response: {dict(session)}")

    return render_template("index.html", response=response)


@app.route("/results")
def show_results():
    results_file = "test_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
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


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
