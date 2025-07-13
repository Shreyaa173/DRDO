# test_login.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://localhost:5173"  # Replace with actual URL

# Enter email used in signup here or import from a config
TEST_EMAIL = "anshikafb1506@gmail.com"
TEST_PASSWORD = "12345"

def test_login():
    service = Service("C:\\Users\\sachi\\DRDO\\DRDO_project\\selenium_tests\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(f"{BASE_URL}/login")
    time.sleep(1)

    driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(TEST_EMAIL)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(3)
    assert "overview" in driver.current_url or "student" in driver.current_url
    print("✅ Login successful")

    driver.quit()

if __name__ == "__main__":
    test_login()
