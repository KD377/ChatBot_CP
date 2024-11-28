# e2e_tests/test_set_years.py

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

class TestSetYears(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        service = ChromeService(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service)
        cls.driver.maximize_window()
        cls.driver.get("http://localhost:3000")
        cls.wait = WebDriverWait(cls.driver, 10) 

    def test_set_years_valid(self):
        driver = self.driver

        years_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".set-years input"))
        )
        years_input.clear()
        years_input.send_keys("2020, 2021, 2022")

        set_years_button = driver.find_element(By.CSS_SELECTOR, ".set-years button")
        set_years_button.click()

        success_message = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".set-years .success"))
        )
        self.assertIn("Zakres lat został ustawiony.", success_message.text)

    def test_set_years_invalid(self):
        driver = self.driver

        years_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".set-years input"))
        )
        years_input.clear()
        years_input.send_keys("1940, 2021")

        set_years_button = driver.find_element(By.CSS_SELECTOR, ".set-years button")
        set_years_button.click()

        error_message = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".set-years .error"))
        )
        self.assertIn("Lata 1940, 1941, 1942, 1943 są niedostępne.", error_message.text)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
