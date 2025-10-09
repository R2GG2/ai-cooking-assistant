import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait      
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys

@pytest.mark.usefixtures("setup_teardown")
class TestRestrictionFilter:
    @pytest.fixture(scope="class")
    def setup_teardown(self, request):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
        driver.get("http://127.0.0.1:5000")

        request.cls.driver = driver
        yield
        driver.quit()

    def send_prompt_and_get_response(self, prompt):
         # Initial warm-up for the first test run
        time.sleep(2)
        input_box = self.driver.find_element(By.ID, "user-input")
        input_box.clear()
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)

                # Wait for placeholder text (case-insensitive)
        WebDriverWait(self.driver, 5).until(
            lambda d: "thinking" in d.find_element(By.ID, "chat-box").text.lower()
        )

        # Wait for placeholder to disappear
        WebDriverWait(self.driver, 10).until(
            lambda d: "thinking" not in d.find_element(By.ID, "chat-box").text.lower()
        )


        chat_box = self.driver.find_element(By.ID, "chat-box")
        return chat_box.text.lower()

    def test_no_pork_restriction(self):
        response = self.send_prompt_and_get_response("I don't eat pork.")
        assert "avoid" in response and "pork" in response, f"AI should acknowledge pork restriction, got: {response}"
        assert "suggest" in response or "alternative" in response, "AI should offer a substitute or safe meal"

    def test_no_dairy_restriction(self):
        response = self.send_prompt_and_get_response("No dairy, please.")
        assert "avoid" in response and "restrict" in response, "AI should mention avoiding restricted items"
        assert "suggest" in response or "substitute" in response, "AI should suggest non-dairy alternatives"

    def test_gluten_free_suggestion(self):
        response = self.send_prompt_and_get_response("Show me gluten-free dinner ideas.")
        assert "gluten" in response, "AI should mention gluten-free context"
        assert any(word in response for word in ["rice", "salad", "soup", "bowl"]), "AI should offer safe staples"

    def test_combined_restrictions(self):
        response = self.send_prompt_and_get_response("No pork and no dairy, please.")
        for restricted in ["pork", "milk", "cheese"]:
            assert restricted in response or "avoid" in response, f"AI should acknowledge restriction: {restricted}"
        assert "healthy" in response or "balanced" in response or "suggest" in response, \
            "AI should reflect thoughtful alternatives"

    def test_unrecognized_restriction(self):
        response = self.send_prompt_and_get_response("Avoid star dust and unicorn meat.")
        assert any(term in response for term in ["avoid", "restricted", "not sure", "unknown"]), \
            "AI should handle unrecognized restrictions gracefully"
