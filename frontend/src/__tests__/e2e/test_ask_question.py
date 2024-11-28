# e2e_tests/test_ask_question.py

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

class TestAskQuestion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        service = ChromeService(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service)
        cls.driver.maximize_window()
        cls.driver.get("http://localhost:3000")
        cls.wait = WebDriverWait(cls.driver, 10)  #

    def test_ask_question_valid(self):
        driver = self.driver

        question_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ask-question textarea"))
        )
        question_input.clear()
        question_input.send_keys("Co to jest kodeks cywilny?")

        ask_question_button = driver.find_element(By.CSS_SELECTOR, ".ask-question button")
        ask_question_button.click()
        answer = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".ask-question .answer"))
        )
        self.assertIn("Odpowiedź:", answer.text)

    def test_ask_question_empty(self):
        driver = self.driver

        question_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ask-question textarea"))
        )
        question_input.clear()

        ask_question_button = driver.find_element(By.CSS_SELECTOR, ".ask-question button")
        ask_question_button.click()

        error_message = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".ask-question .error"))
        )
        self.assertIn("Proszę wpisać pytanie.", error_message.text)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
