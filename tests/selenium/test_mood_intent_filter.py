import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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
        """Send a prompt and return AI response text."""
        time.sleep(1)
        input_box = self.driver.find_element(By.ID, "user-input")
        input_box.clear()
        input_box.send_keys(prompt)
        input_box.send_keys(Keys.RETURN)

        chat_box = self.driver.find_element(By.ID, "chat-box")

        WebDriverWait(self.driver, 12).until(
            lambda d: (
                "thinking" in chat_box.text.lower()
                or (chat_box.text.strip() and len(chat_box.text.strip()) > 20)
            )
        )
        WebDriverWait(self.driver, 20).until_not(
            lambda d: "thinking" in chat_box.text.lower()
        )

        return chat_box.text.lower()

    # --- Mood & Intent Tests ---

    def test_comfort_food_prompt(self, request):
        response = self.send_prompt_and_get_response("I want comfort food.")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["comfort", "cozy", "warm", "hearty"]), \
            f"Expected comfort theme, got: {response}"

    def test_romantic_meal_prompt(self, request):
        response = self.send_prompt_and_get_response("Make something romantic.")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["romantic", "elegant", "date", "candle"]), \
            f"Expected romantic tone, got: {response}"

    def test_quick_dinner_prompt(self, request):
        response = self.send_prompt_and_get_response("I'm short on time. Suggest a quick dinner.")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["quick", "easy", "fast", "15-minute"]), \
            f"Expected quick meal suggestion, got: {response}"

    def test_healthy_reset_prompt(self, request):
        response = self.send_prompt_and_get_response("I need a healthy reset meal.")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["healthy", "light", "fresh", "balanced"]), \
            f"Expected healthy tone, got: {response}"

    def test_intermittent_fasting_prompt(self, request):
        response = self.send_prompt_and_get_response("I'm doing intermittent fasting. What should I eat after my fast?")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["protein", "electrolytes", "nutrient-dense", "replenish", "gentle start"]), \
            f"Expected post-fasting guidance, got: {response}"

    def test_perimenopausal_prompt(self, request):
        response = self.send_prompt_and_get_response("Suggest a meal for a perimenopausal woman.")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["hormone", "balance", "anti-inflammatory", "omega", "fiber"]), \
            f"Expected hormone-aware response, got: {response}"

    def test_bloated_prompt(self, request):
        response = self.send_prompt_and_get_response("I'm feeling bloated. What should I eat?")
        request.node.response_excerpt = response[:250]
        assert any(word in response for word in ["ginger", "mint", "light", "anti-bloat", "soothing"]), \
            f"Expected digestion support, got: {response}"
