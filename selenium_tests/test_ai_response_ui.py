import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
from datetime import datetime
import traceback
import requests

AI_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_app"))
RESULTS_PATH = os.path.join(AI_APP_DIR, "test_results.json")
BASE_URL = "http://127.0.0.1:5000"


def clear_flask_session():
    try:
        response = requests.post(f"{BASE_URL}/clear_session")
        if response.status_code == 200:
            print("Flask session cleared successfully.")
        else:
            print(f"Failed to clear session: {response.status_code}")
    except Exception as e:
        print(f"Error clearing session: {e}")


def setup_driver_and_screenshot(screenshot_name):
    driver = webdriver.Chrome()
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = os.path.join("screenshots", screenshot_name)
    return driver, screenshot_path


def write_test_result(result, filename=RESULTS_PATH):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(result)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def run_selenium_test(test_name, test_func):
    driver, screenshot_path = setup_driver_and_screenshot(f"{test_name}.png")
    status = "pass"
    error = ""

    try:
        test_func(driver)
    except Exception as e:
        status = "fail"
        error = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
    finally:
        driver.save_screenshot(screenshot_path)
        write_test_result(
            {
                "test_name": test_name,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "error": error,
                "screenshot": screenshot_path,
            }
        )
        driver.quit()


def send_input_and_wait(driver, user_text, wait_for_text):
    wait = WebDriverWait(driver, 15)
    input_box = wait.until(EC.presence_of_element_located((By.ID, "user-input")))
    input_box.clear()
    input_box.send_keys(user_text)
    input_box.send_keys(Keys.RETURN)
    wait.until(EC.text_to_be_present_in_element((By.ID, "ai-response"), wait_for_text))
    response_box = driver.find_element(By.ID, "ai-response")
    return response_box.text.lower()


def test_happy_path_response(driver):
    clear_flask_session()
    driver.get(BASE_URL)

    # Step 1: Reply to allergies prompt with "No allergies"
    resp = send_input_and_wait(driver, "No allergies.", "equipment")
    assert "equipment" in resp

    # Step 2: Provide equipment
    resp = send_input_and_wait(driver, "Instant Pot", "ingredients")
    assert "ingredients" in resp

    # Step 3: Provide ingredients
    resp = send_input_and_wait(driver, "chicken, carrots", "suggest")
    print("AI Response (happy path):", resp)

    assert "chicken" in resp
    assert "carrots" in resp
    assert "instant pot" in resp
    assert "suggest" in resp
    assert "avoid" not in resp


def test_restricted_ingredients_response(driver):
    clear_flask_session()
    driver.get(BASE_URL)

    # Step 1: Provide restricted ingredients (expect restriction notice)
    resp = send_input_and_wait(driver, "I have flour, sugar, and turkey.", "avoid")
    assert any(word in resp for word in ["avoid", "restricted"])

    # Step 2: Provide equipment
    resp = send_input_and_wait(driver, "wok", "ingredients")
    assert "ingredients" in resp

    # Step 3: Provide safe ingredients (can be empty or some safe list)
    resp = send_input_and_wait(driver, "chicken, carrots", "suggest")
    print("AI Response (restricted ingredients):", resp)

    assert "avoid" in resp or "suggest" in resp
    assert "flour" not in resp  # Ensure restricted ingredients not suggested


def test_empty_input_response(driver):
    clear_flask_session()
    driver.get(BASE_URL)

    # Provide empty input and expect prompt about allergies/restrictions
    resp = send_input_and_wait(driver, "   ", "allergies")
    print("AI Response (empty input):", resp)

    expected_prompts = [
        "tell me",
        "please",
        "input",
        "allergies",
        "dietary restrictions",
    ]
    assert any(word in resp for word in expected_prompts)


if __name__ == "__main__":
    run_selenium_test("happy_path_response", test_happy_path_response)
    run_selenium_test(
        "restricted_ingredients_response", test_restricted_ingredients_response
    )
    run_selenium_test("empty_input_response", test_empty_input_response)

    print("\nView your test results here: http://127.0.0.1:5000/results\n")
    import webbrowser

    webbrowser.open("http://127.0.0.1:5000/results")
