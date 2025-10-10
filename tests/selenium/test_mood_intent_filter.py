import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


@pytest.mark.usefixtures("setup_teardown")
class TestMoodIntentFilter:
    @pytest.fixture(scope="class")
    def setup_teardown(self, request: pytest.FixtureRequest):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
        driver.get("http://127.0.0.1:5000")
        request.cls.driver = driver
        yield
        driver.quit()

    def send_prompt_and_get_response(self, prompt):
        time.sleep(1)
        input_box = self.driver.find_element(By.ID, "user-input")
        input_box.clear()
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)

        chat_box = self.driver.find_element(By.ID, "chat-box")

        # Wait either for 'thinking' OR first non-empty reply
        WebDriverWait(self.driver, 12).until(
            lambda d: (
                "thinking" in chat_box.text.lower()
                or (chat_box.text.strip() and len(chat_box.text.strip()) > 20)
            )
        )

        # Then wait for final response (no more 'thinking')
        WebDriverWait(self.driver, 20).until_not(
            lambda d: "thinking" in chat_box.text.lower()
        )

        return chat_box.text.lower()

    
    # --- Mood & Intent Tests ---

    def test_comfort_food_prompt(self):
        """AI should respond with cozy, hearty, or comforting tone"""
        response = self.send_prompt_and_get_response("I want comfort food.")
        assert any(word in response for word in ["comfort", "cozy", "warm", "hearty"]), \
            f"Expected comfort theme, got: {response}"

    def test_romantic_meal_prompt(self):
        """AI should suggest romantic, elegant, or fancy meals"""
        response = self.send_prompt_and_get_response("Make something romantic.")
        assert any(word in response for word in ["romantic", "elegant", "date", "candle"]), \
            f"Expected romantic tone, got: {response}"

    def test_quick_dinner_prompt(self):
        """AI should suggest fast or easy meal ideas"""
        response = self.send_prompt_and_get_response("I'm short on time. Suggest a quick dinner.")
        assert any(word in response for word in ["quick", "easy", "fast", "15-minute"]), \
            f"Expected quick meal suggestion, got: {response}"

    def test_healthy_reset_prompt(self):
        """AI should suggest fresh, balanced, or light meals"""
        response = self.send_prompt_and_get_response("I need a healthy reset meal.")
        assert any(word in response for word in ["healthy", "light", "fresh", "balanced"]), \
            f"Expected healthy tone, got: {response}"


    # --- Mood & Intent Tests ---

    def test_comfort_food_prompt(self):
        response = self.send_prompt_and_get_response("I want comfort food.")
        assert any(word in response for word in ["comfort", "cozy", "warm", "hearty"]), \
            f"Expected comfort theme, got: {response}"

    def test_romantic_meal_prompt(self):
        response = self.send_prompt_and_get_response("Make something romantic.")
        assert any(word in response for word in ["romantic", "elegant", "date", "candle"]), \
            f"Expected romantic tone, got: {response}"

    def test_quick_dinner_prompt(self):
        response = self.send_prompt_and_get_response("I'm short on time. Suggest a quick dinner.")
        assert any(word in response for word in ["quick", "easy", "fast", "15-minute"]), \
            f"Expected quick meal suggestion, got: {response}"

    def test_healthy_reset_prompt(self):
        response = self.send_prompt_and_get_response("I need a healthy reset meal.")
        assert any(word in response for word in ["healthy", "light", "fresh", "balanced"]), \
            f"Expected healthy tone, got: {response}"

    # --- Wellness Context Tests ---

    def test_intermittent_fasting_prompt(self):
        """AI should respect fasting window and suggest nutrient-dense meals"""
        response = self.send_prompt_and_get_response("I'm doing intermittent fasting. What should I eat after my fast?")
        assert any(word in response for word in ["protein", "electrolytes", "nutrient-dense", "replenish", "gentle start"]), \
            f"Expected post-fasting guidance, got: {response}"

    def test_perimenopausal_prompt(self):
        """AI should respond with hormone-supportive or anti-inflammatory suggestions"""
        response = self.send_prompt_and_get_response("Suggest a meal for a perimenopausal woman.")
        assert any(word in response for word in ["hormone", "balance", "anti-inflammatory", "omega", "fiber"]), \
            f"Expected hormone-aware response, got: {response}"

    def test_bloated_prompt(self):
        """AI should suggest de-bloating or digestion-friendly options"""
        response = self.send_prompt_and_get_response("I'm feeling bloated. What should I eat?")
        assert any(word in response for word in ["ginger", "mint", "light", "anti-bloat", "soothing"]), \
            f"Expected digestion support, got: {response}"