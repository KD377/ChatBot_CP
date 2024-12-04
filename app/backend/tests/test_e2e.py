import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os


class TestFullFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = ChromeService(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.maximize_window()
        cls.driver.get("http://localhost:3000")
        cls.wait = WebDriverWait(cls.driver, 15)
        os.makedirs("e2e_tests/screenshots", exist_ok=True)

    def test_full_flow_valid(self):
        driver = self.driver

        years_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".set-years input")))
        years_input.clear()
        years_input.send_keys("2020, 2021, 2022")

        set_years_button = driver.find_element(By.CSS_SELECTOR, ".set-years button")
        set_years_button.click()

        success_message = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".set-years .success")))
        self.assertIn("Zakres lat został ustawiony.", success_message.text)

        question_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ask-question textarea")))
        question_input.clear()
        question_input.send_keys("Jakie były zmiany w prawie w ostatnich latach?")

        ask_question_button = driver.find_element(By.CSS_SELECTOR, ".ask-question button")
        ask_question_button.click()

        answer = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ask-question .answer")))
        self.assertIn("Odpowiedź:", answer.text)

    def test_full_flow_invalid_years(self):
        driver = self.driver

        years_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".set-years input")))
        years_input.clear()
        years_input.send_keys("1940, 2021")

        set_years_button = driver.find_element(By.CSS_SELECTOR, ".set-years button")
        set_years_button.click()

        error_message = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".set-years .error")))
        self.assertIn("Lata 1940, 1941, 1942, 1943 są niedostępne.", error_message.text)

    def test_full_flow_empty_question(self):
        driver = self.driver

        years_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".set-years input")))
        years_input.clear()
        years_input.send_keys("2019, 2020")

        set_years_button = driver.find_element(By.CSS_SELECTOR, ".set-years button")
        set_years_button.click()

        success_message = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".set-years .success")))
        self.assertIn("Zakres lat został ustawiony.", success_message.text)

        question_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ask-question textarea")))
        question_input.clear()

        ask_question_button = driver.find_element(By.CSS_SELECTOR, ".ask-question button")
        ask_question_button.click()

        error_message = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ask-question .error")))
        self.assertIn("Proszę wpisać pytanie.", error_message.text)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()