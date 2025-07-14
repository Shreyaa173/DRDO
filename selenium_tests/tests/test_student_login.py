from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
import os

BASE_URL = "http://localhost:5173"
TEST_EMAIL = "anshikafb1506@gmail.com"
TEST_PASSWORD = "12345"

def test_student_login():
    # Resolve path to chromedriver relative to this file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "..", "chromedriver.exe")
    service = Service(CHROMEDRIVER_PATH)

    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    try:
        print("[STEP] Navigating to login page...")
        driver.get(f"{BASE_URL}/login")

        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check if alert appears
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = Alert(driver)
            print("[ERROR] Login alert shown:", alert.text)
            alert.accept()
            print("[FAIL] Login failed due to credentials or server error.")
            return

        except TimeoutException:
            # Alert did not appear, continue to check URL
            wait.until(EC.url_contains("student"))
            print("[SUCCESS] Logged in successfully.")
            print("Current URL:", driver.current_url)

    except Exception as e:
        print("[ERROR] Unexpected Exception:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_student_login()
