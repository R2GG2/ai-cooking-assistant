class TestAIResponseUI(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:5000")

    def tearDown(self):
        time.sleep(2)  # pause to see UI
        self.driver.quit()

    def test_allergy_detection(self):
        input_box = self.driver.find_element(By.ID, "user-input")
        input_box.send_keys("I'm allergic to coconut. I have broccoli and chicken.")
        input_box.send_keys(Keys.RETURN)

        time.sleep(2)
        response = self.driver.find_element(By.ID, "ai-response").text
        print("AI Response (allergy):", response)

        self.assertIn("coconut", response.lower())
        self.assertIn("avoid", response.lower())
        self.assertNotIn("suggest", response.lower())

    def test_happy_path(self):
        input_box = self.driver.find_element(By.ID, "user-input")
        input_box.send_keys("I have chicken, carrots, and an Instant Pot.")
        input_box.send_keys(Keys.RETURN)

        time.sleep(2)
        response = self.driver.find_element(By.ID, "ai-response").text
        print("AI Response (happy):", response)

        self.assertIn("chicken", response.lower())
        self.assertIn("carrots", response.lower())
        self.assertIn("instant pot", response.lower())
        self.assertIn("suggest", response.lower())
        self.assertNotIn("avoid", response.lower())

        self.driver.save_screenshot("happy_path_result.png")

if __name__ == "__main__":
    unittest.main()

