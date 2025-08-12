from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Launch browser
driver = webdriver.Chrome()

# Open lical page
driver.get("http://localhost:8000/test_page.html")


# Find the search box and type query
search_box = driver.find_element(By.ID, "user-input")
search_box.send_keys("AI QA automation with Python")
search_box.send_keys(Keys.RETURN)

# Wait a bit to see the results
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Wait for the search results to be visible (instead of sleeping blindly)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user-input")))


# Optional: Take a screenshot
driver.save_screenshot("search_results.png")

# Close browser
driver.quit()
