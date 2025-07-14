from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from selenium.webdriver.common.alert import Alert
import os

BASE_URL = "http://localhost:5173"
TEST_EMAIL = "anshikafb1506@gmail.com"
TEST_PASSWORD = "12345"

def test_student_login():
    CHROMEDRIVER_PATH = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(f"{BASE_URL}/login")

        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(TEST_EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(TEST_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        try:
            # Wait briefly to see if an alert appears
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = Alert(driver)
            print("[ERROR] Alert Text:", alert.text)
            alert.accept()
            print("[FAIL] Login failed due to incorrect credentials or backend error.")
            return  # Stop the test here if login failed

        except TimeoutException:
            # No alert = likely successful login, so continue
            WebDriverWait(driver, 10).until(
                EC.url_contains("student")
            )
            current_url = driver.current_url
            print("[SUCCESS] Logged in successfully. Current URL:", current_url)

    except Exception as e:
        print("[ERROR] Unexpected Exception:", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    test_student_login()
