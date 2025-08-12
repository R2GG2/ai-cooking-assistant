from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import logging

logging.basicConfig(
    filename="test_ai_planner.log",  # Log file name (will be created in current folder)
    level=logging.INFO,  # Log INFO level and above
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def test_financial_advice_response():
    try:
        logging.info("Starting test: test_financial_advice_response")
        driver = webdriver.Chrome()
        logging.info("Opened Chrome WebDriver")

        driver.get("http://localhost:8000/test_page.html")
        logging.info("Navigated to test page")

        # Simulate user input
        input_box = driver.find_element(By.ID, "user-input")
        input_text = "I make $80,000 a year and want to retire by 50. How much should I invest monthly?"
        input_box.send_keys(input_text)
        input_box.send_keys(Keys.RETURN)
        logging.info(f"Entered user input: {input_text}")

        time.sleep(3)
        logging.info("Waited 3 seconds for AI response")

        # Capture response
        response_box = driver.find_element(By.ID, "ai-response")
        response_text = response_box.text.lower()
        logging.info(f"Captured AI response: {response_text}")

        # Basic checks
        assert (
            "save" in response_text or "invest" in response_text
        ), "No savings advice given"
        logging.info("AI gave savings/investment advice")
        assert (
            "stock" not in response_text
        ), "AI suggested a specific stock, which it shouldn't"
        logging.info("AI did not suggest a specific stock (PASS)")

        print("✅ Test passed!")
        logging.info("Test passed!")

    except Exception as e:
        logging.error(f"Test failed: {e}")
        raise

    finally:
        driver.quit()
        logging.info("Closed Chrome WebDriver")


if __name__ == "__main__":
    test_financial_advice_response()
