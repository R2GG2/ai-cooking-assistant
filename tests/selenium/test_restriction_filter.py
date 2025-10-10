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

    def wait_for_ai_response(driver, timeout=15):
        """Waits for 'Thinking...' to appear and disappear in chat-box, then returns final text."""
        chat_box = driver.find_element(By.ID, "chat-box")

        # Step 1: Wait until 'Thinking' appears
        try:
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.ID, "chat-box"), "Thinking")
            )
        except Exception:
            # if it loads too fast, not a failure — just continue
            pass

        # Step 2: Wait until 'Thinking' disappears or response changes
        WebDriverWait(driver, timeout).until_not(
            EC.text_to_be_present_in_element((By.ID, "chat-box"), "Thinking")
        )

        # Step 3: Grab final text
        return chat_box.text.lower()

    def send_prompt_and_get_response(self, prompt):
        # Warm-up for initial load
        time.sleep(2)

        input_box = self.driver.find_element(By.ID, "user-input")
        input_box.clear()
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)

        chat_box = self.driver.find_element(By.ID, "chat-box")

        try:
            # Wait briefly for "thinking" to appear
            WebDriverWait(self.driver, 5).until(
                lambda d: "thinking" in d.find_element(By.ID, "chat-box").text.lower()
            )
        except:
            print("[StableWait] 'Thinking' skipped — waiting directly for AI response.")

        # Wait until an AI response is visible and 'thinking' gone
        WebDriverWait(self.driver, 20).until(
            lambda d: (
                "ai:" in d.find_element(By.ID, "chat-box").text.lower()
                and "thinking" not in d.find_element(By.ID, "chat-box").text.lower()
            )
)



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
