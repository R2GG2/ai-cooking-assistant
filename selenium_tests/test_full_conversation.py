import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_cooking_assistant_conversation_flow():
    logging.info("Starting full cooking assistant conversation test")

    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/test_page.html")


    wait = WebDriverWait(driver, 10)

    try:
        # Step 1: Vague request
        input_box = wait.until(EC.presence_of_element_located((By.ID, "user-input")))
        input_box.send_keys("I want something cozy for dinner")
        input_box.send_keys(Keys.RETURN)
        time.sleep(2)

        # Step 2: Equipment
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("I have an Instant Pot")
        input_box.send_keys(Keys.RETURN)
        time.sleep(2)

        # Step 3: Dietary restrictions
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("Please avoid flour and sugar")
        input_box.send_keys(Keys.RETURN)
        time.sleep(2)

        # Step 4: Ingredients
        input_box = driver.find_element(By.ID, "user-input")
        input_box.send_keys("I have chicken, carrots, and potatoes")
        input_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Step 5: Validate final response
        response_box = wait.until(EC.presence_of_element_located((By.ID, "ai-response")))
        response_text = response_box.text.lower()
        logging.info(f"Final AI response: {response_text}")

        assert "chicken" in response_text
        assert "instant pot" in response_text
        assert "stew" in response_text or "soup" in response_text

    finally:
        driver.save_screenshot("reports/full_conversation_flow.png")
        driver.quit()
