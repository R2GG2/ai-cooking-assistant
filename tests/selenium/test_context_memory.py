import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.usefixtures("flask_app")
class TestContextMemory:
    """Tests whether the AI assistant remembers context between user messages."""

    @pytest.fixture(scope="class")
    def driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,800")
        driver = webdriver.Chrome(options=options)
        driver.get("http://127.0.0.1:5000")
        yield driver
        driver.quit()

    def send_message_and_wait(self, driver, message):
        """Helper: send message and wait for AI response."""
        input_box = driver.find_element(By.ID, "user-input")
        input_box.clear()
        input_box.send_keys(message)
        input_box.send_keys(Keys.RETURN)

        chat_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "chat-box"))
        )

        # Wait for AI to finish typing (Thinking... disappears)
        WebDriverWait(driver, 15).until_not(
            EC.text_to_be_present_in_element((By.ID, "chat-box"), "Thinking...")
        )

        return chat_box.text.lower()

    # ------------------------------------------------------------------
    # MEMORY TESTS
    # ------------------------------------------------------------------

    def test_remembers_previous_preference(self, driver):
        """Verify AI remembers user dietary restriction between turns."""
        first_response = self.send_message_and_wait(driver, "I don't eat dairy.")
        assert "dairy" in first_response, f"Expected acknowledgment of restriction, got: {first_response}"

        second_response = self.send_message_and_wait(driver, "Give me a pasta recipe.")
        assert "no dairy" in second_response or "non-dairy" in second_response, (
            f"Expected memory of restriction, got: {second_response}"
        )

    def test_recalls_previous_equipment(self, driver):
        """Verify AI remembers equipment context (e.g., Instant Pot)."""
        first_response = self.send_message_and_wait(driver, "I want to use my Instant Pot.")
        assert "instant pot" in first_response, f"Expected mention of Instant Pot, got: {first_response}"

        second_response = self.send_message_and_wait(driver, "Make me a soup.")
        assert "instant pot" in second_response or "pressure cooker" in second_response, (
            f"Expected recall of equipment context, got: {second_response}"
        )

    def test_recalls_prior_mood(self, driver):
        """Verify AI maintains mood context between messages."""
        first_response = self.send_message_and_wait(driver, "I feel tired, make something cozy.")
        assert "cozy" in first_response or "comfort" in first_response, (
            f"Expected comfort tone, got: {first_response}"
        )

        second_response = self.send_message_and_wait(driver, "Add dessert.")
        assert any(word in second_response for word in ["cozy", "comfort", "warm"]), (
            f"Expected mood continuity, got: {second_response}"
        )
