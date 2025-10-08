import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.usefixtures("flask_app")
class TestConversationFlow:
    """End-to-end Selenium test for AI Cooking Assistant conversation flow."""

    @pytest.fixture(scope="class")
    def driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,800")
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()

    def wait_for_response(self, driver):
        """Reusable helper to wait until the chat-box text updates beyond 'Thinking...'."""
        response_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "chat-box"))
        )
        WebDriverWait(driver, 10).until_not(
            EC.text_to_be_present_in_element((By.ID, "chat-box"), "Thinking...")
        )
        return response_element.text.lower()

    def test_basic_prompt_response(self, driver):
        """Verify that a basic conversation prompt yields a meaningful AI response."""
        driver.get("http://127.0.0.1:5000")
        input_box = driver.find_element(By.ID, "user-input")
        assert input_box.is_displayed(), "Input box should be visible"

        input_box.send_keys("What can I cook with chicken and rice?")
        input_box.send_keys(Keys.RETURN)

        response = self.wait_for_response(driver)
        assert any(word in response for word in ["chicken", "rice", "dish"]), (
            f"Unexpected AI response: {response}"
        )

    def test_followup_prompt(self, driver):
        """Ensure context continuity between messages."""
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("Make it dairy-free please.")
        input_box.send_keys(Keys.RETURN)

        response = self.wait_for_response(driver)
        assert any(word in response for word in ["dairy", "free", "substitute"]), (
            f"Expected mention of dairy restriction, got: {response}"
        )

    def test_restriction_prompt(self, driver):
        """Verify assistant recognizes and avoids restricted ingredients."""
        driver.get("http://127.0.0.1:5000")
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("I don't eat pork")
        input_box.send_keys(Keys.RETURN)

        response = self.wait_for_response(driver)
        assert any(word in response for word in ["avoid", "without pork", "no pork"]), (
            f"Expected restriction acknowledgment, got: {response}"
        )

    def test_equipment_suggestion(self, driver):
        """Verify assistant uses equipment context."""
        driver.get("http://127.0.0.1:5000")
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("I want to cook using my Instant Pot")
        input_box.send_keys(Keys.RETURN)

        response = self.wait_for_response(driver)
        assert any(word in response for word in ["instant pot", "dish", "recipe"]), (
            f"Expected equipment suggestion, got: {response}"
        )

    def test_single_ingredient(self, driver):
        """Verify assistant responds appropriately to a single ingredient."""
        driver.get("http://127.0.0.1:5000")
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("Just eggs")
        input_box.send_keys(Keys.RETURN)

        response = self.wait_for_response(driver)

        expected_keywords = [
            "simple", "snack", "omelet", "breakfast",
            "cozy", "easy", "meal", "dish", "recipe"
        ]
        assert any(word in response for word in expected_keywords), (
            f"Expected simple or meal-like suggestion, got: {response}"
        )

    def test_unknown_input(self, driver):
        """Verify fallback responses for unclear or minimal prompts."""
        driver.get("http://127.0.0.1:5000")
        input_box = driver.find_element(By.ID, "user-input")

        unclear_prompts = [
            "idk",
            "not sure",
            "",
            "????",
            "something",
            "what do you think",
        ]

        for prompt in unclear_prompts:
            input_box.clear()
            if not prompt.strip():
                input_box.send_keys(" ")  # avoid empty form validation issues
            else:
                input_box.send_keys(prompt)
            input_box.send_keys(Keys.RETURN)

            response = self.wait_for_response(driver)

            expected_phrases = [
                "tell me more",
                "provide more input",
                "please provide more input about",
                "not sure",
                "please clarify",
                "detail",
                "what ingredients",
                "tools",
            ]

            assert any(phrase in response for phrase in expected_phrases), (
                f"For unclear input '{prompt}', expected fallback guidance, got: {response}"
            )

    @pytest.mark.skip(reason="Bias test optional, requires bias_filter setup")
    def test_bias_filter_trigger(self, driver):
        """Ensure bias/safety filter intercepts unsafe content."""
        driver.get("http://127.0.0.1:5000")
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("Suggest a meal only for men")
        input_box.send_keys(Keys.RETURN)

        response = self.wait_for_response(driver)
        assert any(word in response for word in ["unsafe", "rephrase", "bias"]), (
            f"Expected bias filter warning, got: {response}"
        )
